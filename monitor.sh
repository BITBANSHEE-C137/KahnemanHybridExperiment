#!/usr/bin/env bash
# monitor.sh — Terminal training dashboard (Claude Code theme)
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

# ── Claude Code Theme ────────────────────────────────────────────────────
# Terracotta/coral accent (Claude brand), muted semantic colors
R="\e[0m"
B="\e[1m"
D="\e[2m"

# 256-color palette — warm, minimal, Claude-like
A="\e[38;5;173m"     # accent: terracotta/coral (Claude brand)
T="\e[38;5;255m"     # text: bright white
S="\e[38;5;245m"     # secondary: medium gray
DM="\e[38;5;240m"    # dim: dark gray
G="\e[38;5;114m"     # green: muted sage
Y="\e[38;5;221m"     # yellow: soft amber
RD="\e[38;5;167m"    # red: muted coral-red
C="\e[38;5;110m"     # cyan: muted blue

W=94

sep() {
    printf "  ${DM}"
    printf '%*s' "$W" '' | tr ' ' '─'
    printf "${R}\n"
}

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
        printf "${A}${ticks[$idx]}${R}"
    done
}

pbar() {
    # Progress bar: pbar <value> <max> <width> <color>
    local cur=$1 mx=$2 w=$3 clr=${4:-$G}
    [ "$mx" -eq 0 ] && mx=1
    local filled=$((cur * w / mx)) empty=$((w - filled))
    [ "$filled" -gt "$w" ] && filled=$w && empty=0
    printf "${clr}"
    for ((i=0; i<filled; i++)); do printf "▓"; done
    printf "${DM}"
    for ((i=0; i<empty; i++)); do printf "░"; done
    printf "${R}"
}

gauge() {
    # Compact gauge: gauge <pct> <color> <width>
    local pct=$1 color=$2 w=${3:-10}
    local blocks=(" " "▏" "▎" "▍" "▌" "▋" "▊" "▉" "█")
    local full=$((pct * w / 100)) part=$((pct * w % 100 * 8 / 100))
    [ "$full" -gt "$w" ] && full=$w && part=0
    printf "${color}"
    for ((i=0; i<full; i++)); do printf "█"; done
    [ "$part" -gt 0 ] && [ "$full" -lt "$w" ] && printf "${blocks[$part]}"
    local total=$((full + (part > 0 ? 1 : 0))) rem=$((w - total))
    printf "${DM}"
    for ((i=0; i<rem; i++)); do printf "░"; done
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

trend() {
    local -n arr=$1
    if [ ${#arr[@]} -ge 2 ]; then
        local cmp=$(echo "${arr[-1]} < ${arr[-2]}" | bc -l 2>/dev/null)
        [ "$cmp" = "1" ] && printf " ${G}↓${R}" || printf " ${RD}↑${R}"
    fi
}

# ── Main draw ─────────────────────────────────────────────────────────────
draw() {
    clear
    local now=$(date -u '+%H:%M:%S UTC')

    # ── Header ──
    printf "\n"
    printf "  ${A}${B}◆${R} ${B}${T}ML Training Dashboard${R}  ${DM}${now}${R}\n"

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

    printf "  ${A}◆${R} ${B}Progress${R}\n"
    if [ "$step" -gt 0 ]; then
        local pct=$((step * 100 / MAX_STEPS))
        local phase="cosine decay"
        [ "$step" -le "$WARMUP" ] && phase="warmup"
        local eta_secs=""
        if [ "$elapsed" -gt 0 ]; then
            local sps=$(echo "scale=4; $step / $elapsed" | bc 2>/dev/null)
            eta_secs=$(echo "($MAX_STEPS - $step) / $sps" | bc 2>/dev/null | cut -d. -f1)
        fi

        printf "    ${T}${B}%s${R}${DM}/%s${R}" "$step" "$MAX_STEPS"
        printf "  ${S}%s${R}" "$phase"
        printf "  ${C}$(fmt_time "$elapsed")${R}${S} elapsed${R}"
        [ -n "$eta_secs" ] && printf "  ${Y}$(fmt_time "$eta_secs")${R}${S} remaining${R}"
        printf "\n"
        printf "    "; pbar "$step" "$MAX_STEPS" 76 "$G"; printf " ${B}%d%%${R}\n" "$pct"
    else
        printf "    ${S}Waiting for first step...${R}\n"
    fi

    # ── 2. Metrics ──
    if [ "$step" -gt 0 ]; then
        printf "  ${A}◆${R} ${B}Metrics${R}\n"
        printf "    ${S}AR Loss${R}   ${T}${B}%-8s${R} " "$ar"
        sparkline "${ar_vals[@]}"
        trend ar_vals
        printf "      ${S}Conf Acc${R}  ${T}%s${R}" "$conf"
        printf "\n"
        printf "    ${S}Diff Loss${R} ${T}${B}%-8s${R} " "$diff"
        sparkline "${diff_vals[@]}"
        trend diff_vals
        printf "      ${S}LR${R}        ${T}%s${R}\n" "$lr_val"
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

        # Color thresholds
        local uc="$G"; [ "$gutil" -gt 90 ] && uc="$Y"
        local mc="$G"; [ "$mem_pct" -gt 80 ] && mc="$Y"; [ "$mem_pct" -gt 90 ] && mc="$RD"
        local tc="$G"; [ "${gtemp%.*}" -gt 75 ] && tc="$Y"; [ "${gtemp%.*}" -gt 85 ] && tc="$RD"

        printf "  ${A}◆${R} ${B}GPU${R}  ${DM}%s${R}\n" "$gname"
        printf "    ${S}Util${R}  "; gauge "$gutil" "$uc"; printf " ${B}%s%%${R}" "$gutil"
        printf "      ${S}VRAM${R}  "; gauge "$mem_pct" "$mc"; printf " ${B}%s${R}${DM}/%sG${R}\n" "$mem_gb" "$tot_gb"
        printf "    ${S}Temp${R}  "; gauge "${gtemp%.*}" "$tc"; printf " %b%s°C%b" "$tc" "$gtemp" "$R"
        printf "      ${S}Power${R} "; gauge "$pow_pct" "$G"; printf " ${B}%s${R}${DM}/%sW${R}\n" "${gpow%.*}" "${gpow_lim%.*}"
    fi

    # ── 4. Eval (current run only: step <= current training step) ──
    local eval_data=""
    if [ "$step" -gt 0 ]; then
        eval_data=$(python3 -c "
import json, glob, os
files = glob.glob('$EVAL_DIR/eval_step_*.json')
best = None
for f in files:
    try:
        d = json.load(open(f))
        if d['step'] <= $step and (best is None or d['step'] > best['step']):
            best = d
    except: pass
if best:
    print(f\"{best['step']}|{best['ar_perplexity']:.0f}|{best['s1_token_accuracy']*100:.1f}|{best['conf_auroc']:.3f}|{best['conf_ece']:.4f}|{best['diff_loss']:.4f}\")
" 2>/dev/null)
    fi
    if [ -n "$eval_data" ]; then
        IFS='|' read -r e_step e_ppl e_s1 e_auroc e_ece e_dloss <<< "$eval_data"
        local auroc_pct=$(echo "$e_auroc * 100" | bc 2>/dev/null | cut -d. -f1)
        local ac="$RD"; [ "$auroc_pct" -gt 55 ] && ac="$Y"; [ "$auroc_pct" -gt 70 ] && ac="$G"

        printf "  ${A}◆${R} ${B}Eval${R}  ${DM}step %s${R}\n" "$e_step"
        printf "    ${S}AR PPL${R} ${T}${B}%s${R}" "$e_ppl"
        printf "   ${S}S1 Acc${R} ${T}${B}%s%%${R}" "$e_s1"
        printf "   ${S}AUROC${R} ${T}${B}%s${R} " "$e_auroc"
        gauge "$auroc_pct" "$ac" 6
        printf "   ${S}ECE${R} ${T}%s${R}" "$e_ece"
        printf "   ${S}Diff${R} ${T}%s${R}\n" "$e_dloss"
    else
        local next_eval_step=$(( ((step / EVAL_EVERY) + 1) * EVAL_EVERY ))
        [ "$step" -eq 0 ] && next_eval_step=$EVAL_EVERY
        printf "  ${A}◆${R} ${B}Eval${R}  ${DM}awaiting eval @ step %s${R}\n" "$next_eval_step"
    fi

    # ── 5. Cost ──
    local imds_token=$(curl -sf -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 30" \
        http://169.254.169.254/latest/api/token 2>/dev/null)
    local itype lifecycle az
    if [ -n "$imds_token" ]; then
        itype=$(curl -sf -H "X-aws-ec2-metadata-token: $imds_token" \
            http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null)
        lifecycle=$(curl -sf -H "X-aws-ec2-metadata-token: $imds_token" \
            http://169.254.169.254/latest/meta-data/instance-life-cycle 2>/dev/null)
        az=$(curl -sf -H "X-aws-ec2-metadata-token: $imds_token" \
            http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null)
    fi

    local boot_s=$(date -d "$(uptime -s)" +%s 2>/dev/null)
    local now_s=$(date +%s)
    local uptime_s=$((now_s - boot_s))
    local od_rate="${OD_PRICES[$itype]:-}"

    printf "  ${A}◆${R} ${B}Cost${R}  ${DM}%s · %s · %s · up $(fmt_time "$uptime_s")${R}\n" \
        "${itype:-?}" "${lifecycle:-?}" "${az:-?}"

    if [ -n "$od_rate" ]; then
        local od_cost=$(echo "scale=2; $od_rate * $uptime_s / 3600" | bc 2>/dev/null)
        local od_proj=""
        [ "$step" -gt 0 ] && od_proj=$(echo "scale=6; x=$od_cost / $step * $MAX_STEPS; scale=2; x/1" | bc 2>/dev/null)

        printf "    ${S}On-Demand${R}  \$%s/hr  " "$od_rate"
        printf "${Y}\$%s${R}" "$od_cost"
        [ -n "$od_proj" ] && printf "  ${DM}proj${R} \$%s" "$od_proj"
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

                printf "    ${S}Spot${R}       \$%s/hr  " "$spot_rate"
                printf "${G}\$%s${R}" "$spot_cost"
                [ -n "$spot_proj" ] && printf "  ${DM}proj${R} \$%s" "$spot_proj"
                printf "\n"

                printf "    ${G}Savings${R}    "
                [ -n "$sav_pct" ] && printf "${G}%s%%${R}         " "$sav_pct"
                printf "${G}\$%s${R}" "$savings"
                if [ -n "$od_proj" ] && [ -n "$spot_proj" ]; then
                    local proj_sav=$(echo "scale=2; $od_proj - $spot_proj" | bc 2>/dev/null)
                    printf "  ${DM}proj${R} ${G}\$%s${R}" "$proj_sav"
                fi
                printf "\n"
            fi
        else
            printf "    ${DM}Spot: run update-spot-price.sh to seed data${R}\n"
        fi
    fi

    # ── 6. Infrastructure ──
    local tpid=$(pgrep -f joint_trainer 2>/dev/null | head -1)
    local spid=$(pgrep -f sync-checkpoint 2>/dev/null | head -1)
    local ck_list=$(ls "$CKPT_DIR"/*.pt 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')

    printf "  ${A}◆${R} ${B}Infra${R}  "
    [ -n "$tpid" ] && printf "${G}● trainer${R} " || printf "${RD}○ trainer${R} "
    [ -n "$spid" ] && printf "${G}● sync${R}" || printf "${RD}○ sync${R}"
    printf "\n"

    if [ "$step" -gt 0 ]; then
        local next_eval=$(( ((step / EVAL_EVERY) + 1) * EVAL_EVERY ))
        local next_ckpt=$(( ((step / CKPT_EVERY) + 1) * CKPT_EVERY ))
        printf "    ${DM}next${R} ${S}eval${R} ${C}%s${R} ${DM}in %s${R}" "$next_eval" "$((next_eval - step))"
        printf "  ${S}ckpt${R} ${C}%s${R} ${DM}in %s${R}" "$next_ckpt" "$((next_ckpt - step))"
        [ "$step" -le "$WARMUP" ] && printf "  ${S}warmup ends${R} ${C}%s${R} ${DM}in %s${R}" "$WARMUP" "$((WARMUP - step))"
        printf "\n"
    fi

    printf "    ${DM}ckpts${R} "
    [ -n "$ck_list" ] && printf "${S}%s${R}" "$ck_list" || printf "${DM}none${R}"
    printf "\n"
    printf "    ${DM}config${R} ${S}%s · bs=%s×%s · lr=%s · warmup=%s · eval@%s · ckpt@%s${R}\n" \
        "$MODEL" "$BS" "$GA" "$LR" "$WARMUP" "$EVAL_EVERY" "$CKPT_EVERY"

    # ── 7. Log Tail ──
    sep
    printf "  ${A}◆${R} ${B}Log${R}\n"
    if [ -n "$WANDB_LOG" ] && [ -f "$WANDB_LOG" ]; then
        while IFS= read -r line; do
            # Pick color
            local clr="${DM}"
            [[ "$line" == \[eval\]* ]] && clr="${A}"

            local log_w=$((W - 6))     # 72 usable chars (4 indent + 2 margin)
            local cont_w=$((W - 12))   # 66 for continuation lines

            if [ ${#line} -le "$log_w" ]; then
                printf "    ${clr}%s${R}\n" "$line"
            else
                # Wrap at pipe delimiters
                local first=true remaining="$line" lw=$log_w
                while [ -n "$remaining" ]; do
                    if [ ${#remaining} -le "$lw" ]; then
                        if [ "$first" = true ]; then
                            printf "    ${clr}%s${R}\n" "$remaining"
                        else
                            printf "    ${clr}      %s${R}\n" "$remaining"
                        fi
                        break
                    fi
                    local chunk="${remaining:0:$lw}"
                    local cut_at=$(echo "$chunk" | grep -ob ' | ' | tail -1 | cut -d: -f1)
                    local piece
                    if [ -n "$cut_at" ] && [ "$cut_at" -gt 0 ]; then
                        piece="${remaining:0:$cut_at}"
                        remaining="${remaining:$((cut_at + 3))}"
                    else
                        piece="$chunk"
                        remaining="${remaining:$lw}"
                    fi
                    if [ "$first" = true ]; then
                        printf "    ${clr}%s${R}\n" "$piece"
                        first=false
                        lw=$cont_w
                    else
                        printf "    ${clr}      %s${R}\n" "$piece"
                    fi
                done
            fi
        done < <(tail -6 "$WANDB_LOG")
    else
        printf "    ${DM}No log file found${R}\n"
    fi
    sep
    printf "  ${DM}refresh ${INTERVAL}s${R}  ${DM}q${R}${S}=quit ${DM}r${R}${S}=refresh${R}\n"
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
