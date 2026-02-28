#!/usr/bin/env bash
# monitor.sh — Live training dashboard
# Usage: ./monitor.sh [refresh_seconds]
set -o pipefail
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

INTERVAL="${1:-15}"
PROJECT_DIR="/home/ubuntu/KahnemanHybridExperiment"
WANDB_LOG=$(ls -td "$PROJECT_DIR"/wandb/run-*/files/output.log 2>/dev/null | head -1)
EVAL_DIR="/opt/dlami/nvme/ml-lab/eval_metrics"
CKPT_DIR="/opt/dlami/nvme/ml-lab/checkpoints"
MAX_STEPS=50000

# Colors
R="\e[0m"; B="\e[1m"; D="\e[2m"
Fg="\e[32m"; Fy="\e[33m"; Fr="\e[31m"; Fc="\e[36m"
Fw="\e[97m"; Fk="\e[90m"
Bg="\e[42m"; Br="\e[41m"

W=74

hline() { printf "  ${Fk}"; printf '%*s' "$W" '' | tr ' ' '-'; printf "${R}\n"; }

sparkline() {
    local vals=($@) n=${#vals[@]}
    [ "$n" -eq 0 ] && return
    local ticks=( "▁" "▂" "▃" "▄" "▅" "▆" "▇" "█" )
    local min=999999 max=0
    for v in "${vals[@]}"; do
        local iv=$(echo "$v * 10000" | bc 2>/dev/null | cut -d. -f1)
        [ "$iv" -lt "$min" ] && min=$iv
        [ "$iv" -gt "$max" ] && max=$iv
    done
    local range=$((max - min)); [ "$range" -eq 0 ] && range=1
    for v in "${vals[@]}"; do
        local iv=$(echo "$v * 10000" | bc 2>/dev/null | cut -d. -f1)
        local idx=$(( (iv - min) * 7 / range ))
        printf "${Fc}${ticks[$idx]}${R}"
    done
}

bar() {
    local cur=$1 mx=$2 w=$3
    local filled=$((cur * w / mx)) empty=$((w - filled))
    printf "${Fg}"; for ((i=0; i<filled; i++)); do printf "#"; done
    printf "${Fk}"; for ((i=0; i<empty; i++)); do printf "."; done
    printf "${R}"
}

vbar() {
    local pct=$1 color=$2
    local blocks=( " " "▏" "▎" "▍" "▌" "▋" "▊" "▉" "█" )
    local full=$((pct / 12)) part=$((pct % 12 * 8 / 12))
    printf "${color}"
    for ((i=0; i<full; i++)); do printf "█"; done
    [ "$part" -gt 0 ] && printf "${blocks[$part]}"
    local total=$((full + (part > 0 ? 1 : 0))) rem=$((8 - total))
    printf "${Fk}"; for ((i=0; i<rem; i++)); do printf "·"; done
    printf "${R}"
}

fmt_time() {
    local secs=$1 hrs=$((secs / 3600)) mins=$(( (secs % 3600) / 60 ))
    [ "$hrs" -gt 0 ] && printf "%dh %02dm" "$hrs" "$mins" || printf "%dm" "$mins"
}

trend_arrow() {
    local -n arr=$1
    if [ ${#arr[@]} -ge 2 ]; then
        local cmp=$(echo "${arr[-1]} < ${arr[-2]}" | bc -l 2>/dev/null)
        [ "$cmp" = "1" ] && printf " ${Fg}↓${R}" || printf " ${Fr}↑${R}"
    fi
}

draw() {
    clear
    local now=$(date -u '+%H:%M:%S UTC')

    # ── Header ──
    printf "  ${B}${Fw}KAHNEMAN HYBRID EXPERIMENT${R}  ${Fk}// ${now}${R}   ${D}q${R}=quit  ${D}r${R}=refresh\n"
    hline

    # ── Parse training data ──
    local step=0 ar="" diff="" conf="" lr="" elapsed="0"
    local ar_vals=() diff_vals=()
    if [ -n "$WANDB_LOG" ] && [ -f "$WANDB_LOG" ]; then
        local lines=$(grep '^step:' "$WANDB_LOG")
        local last_line=$(echo "$lines" | tail -1)
        if [ -n "$last_line" ]; then
            step=$(echo "$last_line" | grep -oP 'step: \K[0-9]+')
            ar=$(echo "$last_line" | grep -oP 'ar_loss: \K[0-9.]+')
            diff=$(echo "$last_line" | grep -oP 'diff_loss: \K[0-9.]+')
            conf=$(echo "$last_line" | grep -oP 'conf_acc: \K[0-9.]+')
            lr=$(echo "$last_line" | grep -oP 'lr: \K[0-9.e+-]+')
            elapsed=$(echo "$last_line" | grep -oP 'time: \K[0-9.]+' | cut -d. -f1)
            while IFS= read -r line; do
                local a=$(echo "$line" | grep -oP 'ar_loss: \K[0-9.]+')
                local d=$(echo "$line" | grep -oP 'diff_loss: \K[0-9.]+')
                [ -n "$a" ] && ar_vals+=("$a")
                [ -n "$d" ] && diff_vals+=("$d")
            done <<< "$lines"
        fi
    fi

    # ── Progress + Losses (combined) ──
    if [ "$step" -gt 0 ]; then
        local pct=$((step * 100 / MAX_STEPS))
        printf "  Step ${B}${Fw}%s${R}${D}/%s${R}" "$step" "$MAX_STEPS"
        local active_steps=$((step - 100))
        if [ "$active_steps" -gt 0 ] && [ "$elapsed" -gt 0 ]; then
            local sps=$(echo "scale=2; $elapsed / $active_steps" | bc 2>/dev/null)
            local eta_secs=$(echo "$sps * $((MAX_STEPS - step))" | bc 2>/dev/null | cut -d. -f1)
            printf "  ${Fc}$(fmt_time "$elapsed")${R} elapsed  ${Fy}$(fmt_time "$eta_secs")${R} remaining"
        fi
        printf "\n"
        printf "  ["; bar "$step" "$MAX_STEPS" 50; printf "] ${B}%d%%${R}" "$pct"
        if [ "$step" -lt 2000 ]; then
            printf "  ${Fy}warmup %d%%${R}" "$((step * 100 / 2000))"
        else
            printf "  ${Fg}cosine decay${R}"
        fi
        printf "\n"
        hline

        # Losses — compact 3-line layout
        printf "  ${D}AR  ${R} ${Fw}%-7s${R} " "$ar"
        [ ${#ar_vals[@]} -gt 1 ] && sparkline "${ar_vals[@]}"
        trend_arrow ar_vals
        printf "    ${D}LR${R} %s\n" "$lr"

        printf "  ${D}Diff${R} ${Fw}%-7s${R} " "$diff"
        [ ${#diff_vals[@]} -gt 1 ] && sparkline "${diff_vals[@]}"
        trend_arrow diff_vals
        printf "    ${D}Conf${R} %s" "$conf"
        [ "$conf" = "0.0000" ] && printf " ${Fk}(waiting)${R}"
        printf "\n"
    else
        printf "  ${Fy}Waiting for first training step...${R}\n"
    fi
    hline

    # ── Eval ──
    local latest_eval=$(ls -t "$EVAL_DIR"/*.json 2>/dev/null | head -1)
    if [ -n "$latest_eval" ]; then
        local ej=$(cat "$latest_eval")
        local e_step=$(echo "$ej" | python3 -c "import sys,json; print(json.load(sys.stdin)['step'])" 2>/dev/null)
        local e_ppl=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['ar_perplexity']:.0f}\")" 2>/dev/null)
        local e_s1=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['s1_token_accuracy']*100:.1f}\")" 2>/dev/null)
        local e_auroc=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['conf_auroc']:.3f}\")" 2>/dev/null)
        local e_ece=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['conf_ece']:.4f}\")" 2>/dev/null)

        printf "  ${B}EVAL${R} ${Fk}@%s${R}  " "$e_step"
        printf "PPL ${B}%s${R}  " "$e_ppl"
        printf "S1acc ${B}%s%%${R}  " "$e_s1"
        printf "AUROC ${B}%s${R} [" "$e_auroc"
        local auroc_pct=$(echo "$e_auroc * 100" | bc 2>/dev/null | cut -d. -f1)
        local ac="$Fr"; [ "$auroc_pct" -gt 55 ] && ac="$Fy"; [ "$auroc_pct" -gt 70 ] && ac="$Fg"
        vbar "$auroc_pct" "$ac"
        printf "]  ECE ${B}%s${R}\n" "$e_ece"
    else
        printf "  ${B}EVAL${R}  ${Fk}none yet${R}\n"
    fi
    hline

    # ── GPU — single line with bars ──
    local gpu_csv=$(nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw --format=csv,noheader,nounits 2>/dev/null)
    if [ -n "$gpu_csv" ]; then
        IFS=',' read -r gname gmem_u gmem_t gutil gtemp gpow <<< "$gpu_csv"
        gname=$(echo "$gname" | xargs); gmem_u=$(echo "$gmem_u" | xargs)
        gmem_t=$(echo "$gmem_t" | xargs); gutil=$(echo "$gutil" | xargs)
        gtemp=$(echo "$gtemp" | xargs); gpow=$(echo "$gpow" | xargs)
        local mem_pct=$((gmem_u * 100 / gmem_t))
        local mem_gb=$(echo "scale=1; $gmem_u / 1024" | bc 2>/dev/null)
        local tot_gb=$(echo "scale=0; $gmem_t / 1024" | bc 2>/dev/null)
        local mc="$Fg"; [ "$mem_pct" -gt 80 ] && mc="$Fy"; [ "$mem_pct" -gt 90 ] && mc="$Fr"
        local tc="$Fg"; [ "$gtemp" -gt 75 ] && tc="$Fy"; [ "$gtemp" -gt 85 ] && tc="$Fr"

        printf "  ${B}GPU${R} ${Fk}%s${R}  " "$gname"
        printf "VRAM ["; vbar "$mem_pct" "$mc"; printf "] ${B}%s${R}/%sG  " "$mem_gb" "$tot_gb"
        printf "Util ${B}%s%%${R}  " "$gutil"
        printf "%b%s°C%b  " "$tc" "$gtemp" "$R"
        printf "${Fk}%sW${R}\n" "$gpow"
    fi
    hline

    # ── Infra — compact ──
    local tpid=$(pgrep -f joint_trainer 2>/dev/null | head -1)
    local spid=$(pgrep -f sync-checkpoint 2>/dev/null | head -1)
    local ck_n=$(ls "$CKPT_DIR"/*.pt 2>/dev/null | wc -l)
    local next_ckpt=$(( ((step / 5000) + 1) * 5000 ))
    local next_eval=$(( ((step / 1000) + 1) * 1000 ))

    printf "  "
    [ -n "$tpid" ] && printf "Train ${Bg}${B} ON ${R} " || printf "Train ${Br}${B} OFF ${R} "
    [ -n "$spid" ] && printf "Sync ${Bg}${B} ON ${R} " || printf "Sync ${Br}${B} OFF ${R} "
    printf " ${Fk}Ckpts:%s  NextCkpt:%s  NextEval:%s${R}\n" "$ck_n" "$next_ckpt" "$next_eval"
    hline
}

# Key input handling — non-blocking read during sleep
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

trap 'printf "\n"; exit 0' INT TERM
# Hide cursor
printf "\e[?25l"
trap 'printf "\e[?25h\n"; exit 0' EXIT

while true; do
    draw
    wait_with_keys "$INTERVAL"
done
