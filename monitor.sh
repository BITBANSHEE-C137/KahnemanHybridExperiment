#!/usr/bin/env bash
# monitor.sh — Terminal training dashboard
# Mirrors the web dashboard (web_dashboard.py) as a terminal UI.
# Same data sources, same section order, same metrics.
#
# Usage: ./monitor.sh [refresh_seconds]
set -o pipefail
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

INTERVAL="${1:-15}"

# ── Configuration (matches web_dashboard.py) ─────────────────────────────
PROJECT_DIR="/home/ubuntu/KahnemanHybridExperiment"
DATA_DIR="/opt/dlami/nvme/ml-lab"
EVAL_DIR="$DATA_DIR/eval_metrics"
CKPT_DIR="$DATA_DIR/checkpoints"
CONFIG="$PROJECT_DIR/configs/tiny.yaml"
SPOT_PRICE_FILE="/tmp/spot_price.json"

# Read config
MAX_STEPS=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['training']['max_steps'])" 2>/dev/null || echo 50000)
WARMUP=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['training']['warmup_steps'])" 2>/dev/null || echo 2000)
EVAL_EVERY=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['training']['eval_every'])" 2>/dev/null || echo 1000)
CKPT_EVERY=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['training']['checkpoint_every'])" 2>/dev/null || echo 5000)
LR=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['training']['learning_rate'])" 2>/dev/null || echo "3e-4")
BS=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['training']['batch_size'])" 2>/dev/null || echo 4)
GA=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['training']['gradient_accumulation_steps'])" 2>/dev/null || echo 8)
MODEL=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG')); print(c['model']['name'])" 2>/dev/null || echo "gpt2")

# On-demand prices
declare -A OD_PRICES=( ["g6.xlarge"]="0.8048" ["g6.2xlarge"]="0.9776" ["g5.xlarge"]="1.006" )

# Find W&B log
WANDB_LOG=$(ls -td "$PROJECT_DIR"/wandb/run-*/files/output.log 2>/dev/null | head -1)

# ── Colors ────────────────────────────────────────────────────────────────
R="\e[0m"; B="\e[1m"; D="\e[2m"
Fg="\e[32m"; Fy="\e[33m"; Fr="\e[31m"; Fc="\e[36m"
Fw="\e[97m"; Fk="\e[90m"; Fm="\e[35m"
Bg="\e[42m"; Br="\e[41m"

W=78

hline() { printf "  ${Fk}"; printf '%*s' "$W" '' | tr ' ' '─'; printf "${R}\n"; }

# ── Drawing helpers ───────────────────────────────────────────────────────
sparkline() {
    local vals=("$@") n=${#vals[@]}
    [ "$n" -eq 0 ] && return
    local ticks=("▁" "▂" "▃" "▄" "▅" "▆" "▇" "█")
    local min=999999999 max=0
    for v in "${vals[@]}"; do
        local iv=$(echo "$v * 100000" | bc 2>/dev/null | cut -d. -f1)
        [ -z "$iv" ] && continue
        [ "$iv" -lt "$min" ] && min=$iv
        [ "$iv" -gt "$max" ] && max=$iv
    done
    local range=$((max - min)); [ "$range" -eq 0 ] && range=1
    for v in "${vals[@]}"; do
        local iv=$(echo "$v * 100000" | bc 2>/dev/null | cut -d. -f1)
        [ -z "$iv" ] && continue
        local idx=$(( (iv - min) * 7 / range ))
        printf "${Fc}${ticks[$idx]}${R}"
    done
}

bar() {
    local cur=$1 mx=$2 w=$3
    [ "$mx" -eq 0 ] && mx=1
    local filled=$((cur * w / mx)) empty=$((w - filled))
    [ "$filled" -gt "$w" ] && filled=$w && empty=0
    printf "${Fg}"; for ((i=0; i<filled; i++)); do printf "█"; done
    printf "${Fk}"; for ((i=0; i<empty; i++)); do printf "░"; done
    printf "${R}"
}

vbar() {
    local pct=$1 color=$2 w=${3:-8}
    local blocks=(" " "▏" "▎" "▍" "▌" "▋" "▊" "▉" "█")
    local full=$((pct * w / 100)) part=$((pct * w % 100 * 8 / 100))
    [ "$full" -gt "$w" ] && full=$w && part=0
    printf "${color}"
    for ((i=0; i<full; i++)); do printf "█"; done
    [ "$part" -gt 0 ] && [ "$full" -lt "$w" ] && printf "${blocks[$part]}"
    local total=$((full + (part > 0 ? 1 : 0))) rem=$((w - total))
    printf "${Fk}"; for ((i=0; i<rem; i++)); do printf "·"; done
    printf "${R}"
}

fmt_time() {
    local secs=${1:-0}
    secs=${secs%.*}
    local hrs=$((secs / 3600)) mins=$(( (secs % 3600) / 60 ))
    if [ "$hrs" -gt 0 ]; then
        printf "%dh %dm" "$hrs" "$mins"
    else
        printf "%dm" "$mins"
    fi
}

trend_arrow() {
    local -n arr=$1
    if [ ${#arr[@]} -ge 2 ]; then
        local cmp=$(echo "${arr[-1]} < ${arr[-2]}" | bc -l 2>/dev/null)
        [ "$cmp" = "1" ] && printf " ${Fg}↓${R}" || printf " ${Fr}↑${R}"
    fi
}

right_align() {
    # Print text right-aligned to column W+2
    local text="$1" stripped
    stripped=$(echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g')
    local len=${#stripped}
    local pad=$((W + 2 - len))
    [ "$pad" -gt 0 ] && printf '%*s' "$pad" ''
    printf "%b" "$text"
}

# ── Main draw ─────────────────────────────────────────────────────────────
draw() {
    clear
    local now=$(date -u '+%H:%M:%S UTC')

    # ── Header ──
    printf "  ${B}${Fw}ML TRAINING DASHBOARD${R}  ${Fk}${now}${R}"
    printf "%*s" $((W - 36)) ""
    printf "${Fk}q${R}=quit  ${Fk}r${R}=refresh\n"
    hline

    # ── 1. Training Progress ──
    local step=0 ar="" diff="" conf="" lr_val="" elapsed="0"
    local ar_vals=() diff_vals=() conf_vals=() lr_vals=()
    if [ -n "$WANDB_LOG" ] && [ -f "$WANDB_LOG" ]; then
        local lines=$(grep '^step:' "$WANDB_LOG")
        local last_line=$(echo "$lines" | tail -1)
        if [ -n "$last_line" ]; then
            step=$(echo "$last_line" | grep -oP 'step: \K[0-9]+')
            ar=$(echo "$last_line" | grep -oP 'ar_loss: \K[0-9.]+')
            diff=$(echo "$last_line" | grep -oP 'diff_loss: \K[0-9.]+')
            conf=$(echo "$last_line" | grep -oP 'conf_acc: \K[0-9.]+')
            lr_val=$(echo "$last_line" | grep -oP 'lr: \K[0-9.e+-]+')
            elapsed=$(echo "$last_line" | grep -oP 'time: \K[0-9.]+' | cut -d. -f1)
            # Collect history for sparklines (last 30)
            local tail_lines=$(echo "$lines" | tail -30)
            while IFS= read -r line; do
                local a=$(echo "$line" | grep -oP 'ar_loss: \K[0-9.]+')
                local d=$(echo "$line" | grep -oP 'diff_loss: \K[0-9.]+')
                local c=$(echo "$line" | grep -oP 'conf_acc: \K[0-9.]+')
                local l=$(echo "$line" | grep -oP 'lr: \K[0-9.e+-]+')
                [ -n "$a" ] && ar_vals+=("$a")
                [ -n "$d" ] && diff_vals+=("$d")
                [ -n "$c" ] && conf_vals+=("$c")
                [ -n "$l" ] && lr_vals+=("$l")
            done <<< "$tail_lines"
        fi
    fi

    printf "  ${B}PROGRESS${R}  "
    if [ "$step" -gt 0 ]; then
        local pct=$((step * 100 / MAX_STEPS))
        local phase="cosine_decay"
        [ "$step" -le "$WARMUP" ] && phase="warmup"
        local eta_secs=""
        if [ "$elapsed" -gt 0 ]; then
            local sps=$(echo "scale=4; $step / $elapsed" | bc 2>/dev/null)
            eta_secs=$(echo "($MAX_STEPS - $step) / $sps" | bc 2>/dev/null | cut -d. -f1)
        fi

        printf "Step ${B}${Fw}%s${R}${Fk}/%s${R}" "$step" "$MAX_STEPS"
        printf "  Phase: ${B}%s${R}" "$phase"
        printf "  Elapsed: ${Fc}$(fmt_time "$elapsed")${R}"
        [ -n "$eta_secs" ] && printf "  Remaining: ${Fy}$(fmt_time "$eta_secs")${R}"
        printf "\n"
        printf "  ["; bar "$step" "$MAX_STEPS" 54; printf "] ${B}%d%%${R}\n" "$pct"
    else
        printf "${Fy}Waiting for first training step...${R}\n"
    fi
    hline

    # ── 2. Live Metrics ──
    if [ "$step" -gt 0 ]; then
        printf "  ${B}METRICS${R}\n"
        printf "  AR Loss  ${Fw}%-8s${R} " "$ar"
        sparkline "${ar_vals[@]}"
        trend_arrow ar_vals
        printf "     Conf Acc  ${Fw}%s${R}" "$conf"
        [ "$conf" = "0.0000" ] && printf " ${Fk}(waiting)${R}"
        printf "\n"

        printf "  Diff Loss ${Fw}%-8s${R} " "$diff"
        sparkline "${diff_vals[@]}"
        trend_arrow diff_vals
        printf "     LR       ${Fw}%s${R}\n" "$lr_val"
        hline
    fi

    # ── 3. GPU ──
    local gpu_csv=$(nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,power.limit --format=csv,noheader,nounits 2>/dev/null)
    if [ -n "$gpu_csv" ]; then
        IFS=',' read -r gname gmem_u gmem_t gutil gtemp gpow gpow_lim <<< "$gpu_csv"
        gname=$(echo "$gname" | xargs); gmem_u=$(echo "$gmem_u" | xargs)
        gmem_t=$(echo "$gmem_t" | xargs); gutil=$(echo "$gutil" | xargs)
        gtemp=$(echo "$gtemp" | xargs); gpow=$(echo "$gpow" | xargs)
        gpow_lim=$(echo "$gpow_lim" | xargs)
        local mem_pct=$((gmem_u * 100 / gmem_t))
        local mem_gb=$(echo "scale=1; $gmem_u / 1024" | bc 2>/dev/null)
        local tot_gb=$(echo "scale=0; $gmem_t / 1024" | bc 2>/dev/null)
        local pow_pct=$((${gpow%.*} * 100 / ${gpow_lim%.*}))
        local mc="$Fg"; [ "$mem_pct" -gt 80 ] && mc="$Fy"; [ "$mem_pct" -gt 90 ] && mc="$Fr"
        local tc="$Fg"; [ "${gtemp%.*}" -gt 75 ] && tc="$Fy"; [ "${gtemp%.*}" -gt 85 ] && tc="$Fr"
        local uc="$Fg"; [ "$gutil" -gt 90 ] && uc="$Fy"

        printf "  ${B}GPU${R}  ${Fk}%s${R}\n" "$gname"
        printf "  Util ["; vbar "$gutil" "$uc"; printf "] ${B}%s%%${R}" "$gutil"
        printf "     VRAM ["; vbar "$mem_pct" "$mc"; printf "] ${B}%s${R}/%sG\n" "$mem_gb" "$tot_gb"
        printf "  Temp ["; vbar "${gtemp%.*}" "$tc"; printf "] %b%s°C%b" "$tc" "$gtemp" "$R"
        printf "     Power ["; vbar "$pow_pct" "$Fg"; printf "] ${B}%s${R}/%sW\n" "${gpow%.*}" "${gpow_lim%.*}"
        hline
    fi

    # ── 4. Loss Curves / Eval (charts equivalent) ──
    local latest_eval=$(ls -t "$EVAL_DIR"/*.json 2>/dev/null | head -1)
    if [ -n "$latest_eval" ]; then
        local ej=$(cat "$latest_eval")
        local e_step=$(echo "$ej" | python3 -c "import sys,json; print(json.load(sys.stdin)['step'])" 2>/dev/null)
        local e_ppl=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['ar_perplexity']:.0f}\")" 2>/dev/null)
        local e_s1=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['s1_token_accuracy']*100:.1f}\")" 2>/dev/null)
        local e_auroc=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['conf_auroc']:.3f}\")" 2>/dev/null)
        local e_ece=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['conf_ece']:.4f}\")" 2>/dev/null)
        local e_dloss=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['diff_loss']:.4f}\")" 2>/dev/null)
        local auroc_pct=$(echo "$e_auroc * 100" | bc 2>/dev/null | cut -d. -f1)
        local ac="$Fr"; [ "$auroc_pct" -gt 55 ] && ac="$Fy"; [ "$auroc_pct" -gt 70 ] && ac="$Fg"

        printf "  ${B}EVAL${R} ${Fk}@step %s${R}\n" "$e_step"
        printf "  AR PPL ${B}${Fw}%s${R}  " "$e_ppl"
        printf "S1 Acc ${B}%s%%${R}  " "$e_s1"
        printf "AUROC ${B}%s${R} [" "$e_auroc"
        vbar "$auroc_pct" "$ac" 6
        printf "]  ECE ${B}%s${R}  " "$e_ece"
        printf "Diff ${B}%s${R}\n" "$e_dloss"
    else
        printf "  ${B}EVAL${R}  ${Fk}no eval data yet${R}\n"
    fi
    hline

    # ── 5. Instance & Cost ──
    local itype=$(curl -sf -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 30" \
        http://169.254.169.254/latest/api/token 2>/dev/null | \
        xargs -I{} curl -sf -H "X-aws-ec2-metadata-token: {}" \
        http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null)
    local lifecycle=$(curl -sf -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 30" \
        http://169.254.169.254/latest/api/token 2>/dev/null | \
        xargs -I{} curl -sf -H "X-aws-ec2-metadata-token: {}" \
        http://169.254.169.254/latest/meta-data/instance-life-cycle 2>/dev/null)
    local az=$(curl -sf -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 30" \
        http://169.254.169.254/latest/api/token 2>/dev/null | \
        xargs -I{} curl -sf -H "X-aws-ec2-metadata-token: {}" \
        http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null)

    local boot_s=$(date -d "$(uptime -s)" +%s 2>/dev/null)
    local now_s=$(date +%s)
    local uptime_s=$((now_s - boot_s))
    local od_rate="${OD_PRICES[$itype]:-}"

    printf "  ${B}COST${R}  ${Fk}%s  %s  %s${R}  up ${Fw}$(fmt_time "$uptime_s")${R}\n" \
        "${itype:-?}" "${lifecycle:-?}" "${az:-?}"

    if [ -n "$od_rate" ]; then
        local od_cost=$(echo "scale=2; $od_rate * $uptime_s / 3600" | bc 2>/dev/null)
        local od_proj=""
        [ "$step" -gt 0 ] && od_proj=$(echo "scale=6; x=$od_cost / $step * $MAX_STEPS; scale=2; x/1" | bc 2>/dev/null)

        printf "  %-10s ${Fk}Rate${R} \$%-10s ${Fk}Cost${R} " "On-Demand" "${od_rate}/hr"
        printf "${Fy}\$%-8s${R}" "$od_cost"
        [ -n "$od_proj" ] && printf " ${Fk}Proj${R} \$%s" "$od_proj"
        printf "\n"

        # Spot
        if [ -f "$SPOT_PRICE_FILE" ]; then
            local spot_rate=$(python3 -c "import json; print(json.load(open('$SPOT_PRICE_FILE')).get('current_price',''))" 2>/dev/null)
            if [ -n "$spot_rate" ]; then
                local spot_cost=$(python3 -c "
import json
from datetime import datetime, timezone
d = json.load(open('$SPOT_PRICE_FILE'))
hist = sorted(d.get('price_history', []), key=lambda x: x['timestamp'])
boot_ts = $boot_s
now_ts = $now_s
total = 0.0
for i, seg in enumerate(hist):
    s = max(seg['timestamp'], boot_ts)
    e = hist[i+1]['timestamp'] if i+1 < len(hist) else now_ts
    e = min(e, now_ts)
    if s < e:
        total += seg['price'] * (e - s) / 3600
print(f'{total:.2f}')
" 2>/dev/null)
                local spot_proj=""
                [ "$step" -gt 0 ] && spot_proj=$(echo "scale=6; x=$spot_cost / $step * $MAX_STEPS; scale=2; x/1" | bc 2>/dev/null)
                local savings=$(echo "scale=2; $od_cost - $spot_cost" | bc 2>/dev/null)
                local sav_pct=""
                [ "$(echo "$od_cost > 0" | bc)" = "1" ] && sav_pct=$(echo "scale=1; (1 - $spot_cost / $od_cost) * 100" | bc 2>/dev/null)

                printf "  %-10s ${Fk}Rate${R} \$%-10s ${Fk}Cost${R} " "Spot" "${spot_rate}/hr"
                printf "${Fg}\$%-8s${R}" "$spot_cost"
                [ -n "$spot_proj" ] && printf " ${Fk}Proj${R} \$%s" "$spot_proj"
                printf "\n"
                printf "  ${Fg}%-10s${R}" "Savings"
                [ -n "$sav_pct" ] && printf " ${Fg}%s%%${R}%*s" "$sav_pct" 13 ""
                printf " ${Fg}\$%-8s${R}" "$savings"
                if [ -n "$od_proj" ] && [ -n "$spot_proj" ]; then
                    local proj_sav=$(echo "scale=2; $od_proj - $spot_proj" | bc 2>/dev/null)
                    printf " ${Fk}Proj${R} ${Fg}\$%s${R}" "$proj_sav"
                fi
                printf "\n"
            fi
        else
            printf "  ${Fk}Spot       run update-spot-price.sh to seed spot data${R}\n"
        fi
    fi
    hline

    # ── 6. Infrastructure ──
    local tpid=$(pgrep -f joint_trainer 2>/dev/null | head -1)
    local spid=$(pgrep -f sync-checkpoint 2>/dev/null | head -1)
    local ck_n=$(ls "$CKPT_DIR"/*.pt 2>/dev/null | wc -l)
    local ck_list=$(ls "$CKPT_DIR"/*.pt 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')

    printf "  ${B}INFRA${R}  "
    [ -n "$tpid" ] && printf "${Bg}${B} Trainer ON ${R} " || printf "${Br}${B} Trainer OFF ${R} "
    [ -n "$spid" ] && printf "${Bg}${B} Sync ON ${R}" || printf "${Br}${B} Sync OFF ${R}"
    printf "\n"

    # Milestones
    if [ "$step" -gt 0 ]; then
        local next_eval=$(( ((step / EVAL_EVERY) + 1) * EVAL_EVERY ))
        local next_ckpt=$(( ((step / CKPT_EVERY) + 1) * CKPT_EVERY ))
        printf "  ${Fk}Next:${R} eval @${Fc}%s${R} ${Fk}(in %s)${R}" "$next_eval" "$((next_eval - step))"
        printf "  ckpt @${Fc}%s${R} ${Fk}(in %s)${R}" "$next_ckpt" "$((next_ckpt - step))"
        [ "$step" -le "$WARMUP" ] && printf "  warmup ends @${Fc}%s${R} ${Fk}(in %s)${R}" "$WARMUP" "$((WARMUP - step))"
        printf "\n"
    fi

    # Checkpoints
    printf "  ${Fk}Ckpts:${R} "
    [ -n "$ck_list" ] && printf "%s" "$ck_list" || printf "${Fk}none${R}"
    printf "\n"

    # Config
    printf "  ${Fk}Config:${R} %s | bs=%s×%s | lr=%s | warmup=%s | eval@%s | ckpt@%s\n" \
        "$MODEL" "$BS" "$GA" "$LR" "$WARMUP" "$EVAL_EVERY" "$CKPT_EVERY"
    hline

    # ── 7. Log Tail ──
    printf "  ${B}LOG${R}\n"
    if [ -n "$WANDB_LOG" ] && [ -f "$WANDB_LOG" ]; then
        tail -10 "$WANDB_LOG" | while IFS= read -r line; do
            if [[ "$line" == \[eval\]* ]]; then
                printf "  ${Fy}%s${R}\n" "$line"
            else
                printf "  %s\n" "$line"
            fi
        done
    else
        printf "  ${Fk}No log file found${R}\n"
    fi
    hline
    printf "  ${Fk}Refresh: ${INTERVAL}s${R}\n"
}

# ── Key handling ──────────────────────────────────────────────────────────
wait_with_keys() {
    local remaining=$1
    while [ "$remaining" -gt 0 ]; do
        if read -rsn1 -t 1 key 2>/dev/null; then
            case "$key" in
                q|Q) printf "\n"; exit 0 ;;
                r|R) return 0 ;;
            esac
        fi
        remaining=$((remaining - 1))
    done
}

trap 'printf "\e[?25h\n"; exit 0' INT TERM EXIT
printf "\e[?25l"  # hide cursor

while true; do
    draw
    wait_with_keys "$INTERVAL"
done
