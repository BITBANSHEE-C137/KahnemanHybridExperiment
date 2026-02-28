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
R="\e[0m"      # reset
B="\e[1m"      # bold
D="\e[2m"      # dim
UL="\e[4m"     # underline
Fg="\e[32m"    # green
Fy="\e[33m"    # yellow
Fr="\e[31m"    # red
Fc="\e[36m"    # cyan
Fm="\e[35m"    # magenta
Fw="\e[97m"    # bright white
Bg="\e[42m"    # green bg
Br="\e[41m"    # red bg
By="\e[43m"    # yellow bg
Fk="\e[90m"    # dark gray

# Box drawing (ASCII safe)
H="-"; V="|"; TL="+"; TR="+"; BL="+"; BR="+"
# Try unicode if terminal supports it
if printf '\xe2\x94\x80' 2>/dev/null | grep -qP '\x{2500}' 2>/dev/null; then
    H="\xe2\x94\x80"; V="\xe2\x94\x82"
    TL="\xe2\x94\x8c"; TR="\xe2\x94\x90"
    BL="\xe2\x94\x94"; BR="\xe2\x94\x98"
fi

W=74  # width

hline() {
    printf "  ${Fk}"
    printf '%*s' "$W" '' | tr ' ' '-'
    printf "${R}\n"
}

sparkline() {
    # Generate a mini sparkline from space-separated values
    local vals=($@)
    local n=${#vals[@]}
    [ "$n" -eq 0 ] && return
    local ticks=( "▁" "▂" "▃" "▄" "▅" "▆" "▇" "█" )
    local min=999999 max=0
    for v in "${vals[@]}"; do
        local iv=$(echo "$v * 10000" | bc 2>/dev/null | cut -d. -f1)
        [ "$iv" -lt "$min" ] && min=$iv
        [ "$iv" -gt "$max" ] && max=$iv
    done
    local range=$((max - min))
    [ "$range" -eq 0 ] && range=1
    for v in "${vals[@]}"; do
        local iv=$(echo "$v * 10000" | bc 2>/dev/null | cut -d. -f1)
        local idx=$(( (iv - min) * 7 / range ))
        printf "${Fc}${ticks[$idx]}${R}"
    done
}

bar() {
    # Progress bar: bar <current> <max> <width>
    local cur=$1 mx=$2 w=$3
    local pct=$((cur * 100 / mx))
    local filled=$((cur * w / mx))
    local empty=$((w - filled))
    printf "${Fg}"
    for ((i=0; i<filled; i++)); do printf "#"; done
    printf "${Fk}"
    for ((i=0; i<empty; i++)); do printf "."; done
    printf "${R}"
}

vbar() {
    # Vertical meter: vbar <pct> <color>
    local pct=$1 color=$2
    local blocks=( " " "▏" "▎" "▍" "▌" "▋" "▊" "▉" "█" )
    local full=$((pct / 12))
    local part=$((pct % 12 * 8 / 12))
    printf "${color}"
    for ((i=0; i<full; i++)); do printf "█"; done
    [ "$part" -gt 0 ] && printf "${blocks[$part]}"
    local total=$((full + (part > 0 ? 1 : 0)))
    local rem=$((8 - total))
    printf "${Fk}"
    for ((i=0; i<rem; i++)); do printf "·"; done
    printf "${R}"
}

fmt_time() {
    local secs=$1
    local hrs=$((secs / 3600))
    local mins=$(( (secs % 3600) / 60 ))
    if [ "$hrs" -gt 0 ]; then
        printf "%dh %02dm" "$hrs" "$mins"
    else
        printf "%dm" "$mins"
    fi
}

draw() {
    clear
    local now=$(date -u '+%H:%M:%S UTC')
    local today=$(date -u '+%Y-%m-%d')

    # ── Header ──
    printf "\n"
    printf "  ${B}${Fw}KAHNEMAN HYBRID EXPERIMENT${R}  ${D}${Fk}// training monitor // ${today} ${now}${R}\n"
    printf "  ${D}Refresh: ${INTERVAL}s${R}  ${D}|${R}  ${D}Ctrl-C exit${R}\n"
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

            # Collect all values for sparklines
            while IFS= read -r line; do
                local a=$(echo "$line" | grep -oP 'ar_loss: \K[0-9.]+')
                local d=$(echo "$line" | grep -oP 'diff_loss: \K[0-9.]+')
                [ -n "$a" ] && ar_vals+=("$a")
                [ -n "$d" ] && diff_vals+=("$d")
            done <<< "$lines"
        fi
    fi

    # ── Progress ──
    if [ "$step" -gt 0 ]; then
        local pct=$((step * 100 / MAX_STEPS))
        printf "\n"
        printf "  ${B}PROGRESS${R}\n\n"
        printf "  Step ${B}${Fw}%s${R} ${D}of${R} %s" "$step" "$MAX_STEPS"

        # ETA calc
        local active_steps=$((step - 100))
        if [ "$active_steps" -gt 0 ] && [ "$elapsed" -gt 0 ]; then
            local sps=$(echo "scale=2; $elapsed / $active_steps" | bc 2>/dev/null)
            local rem_steps=$((MAX_STEPS - step))
            local eta_secs=$(echo "$sps * $rem_steps" | bc 2>/dev/null | cut -d. -f1)
            local elapsed_fmt=$(fmt_time "$elapsed")
            local eta_fmt=$(fmt_time "$eta_secs")
            printf "  ${D}|${R}  elapsed ${Fc}${elapsed_fmt}${R}  ${D}|${R}  remaining ${Fy}${eta_fmt}${R}"
        fi
        printf "\n\n"

        # Progress bar
        printf "  ["
        bar "$step" "$MAX_STEPS" 50
        printf "] ${B}%d%%${R}\n" "$pct"

        # Phase indicator
        if [ "$step" -lt 2000 ]; then
            local wp=$((step * 100 / 2000))
            printf "  ${D}Phase: ${Fy}LR Warmup${R} ${D}(%d%%)${R}\n" "$wp"
        else
            printf "  ${D}Phase: ${Fg}Cosine Decay${R}\n"
        fi

        hline

        # ── Losses ──
        printf "\n"
        printf "  ${B}LOSSES${R}\n\n"

        # AR Loss
        local ar_color="$Fw"
        printf "  ${D}AR (System 2)${R}      %b%-8s%b" "$ar_color" "$ar" "$R"
        if [ ${#ar_vals[@]} -gt 1 ]; then
            printf "  "
            sparkline "${ar_vals[@]}"
        fi

        # Trend arrow
        if [ ${#ar_vals[@]} -ge 2 ]; then
            local prev="${ar_vals[-2]}"
            local curr="${ar_vals[-1]}"
            local cmp=$(echo "$curr < $prev" | bc -l 2>/dev/null)
            if [ "$cmp" = "1" ]; then
                printf " ${Fg}↓${R}"
            else
                printf " ${Fr}↑${R}"
            fi
        fi
        printf "\n"

        # Diff Loss
        local diff_color="$Fw"
        printf "  ${D}Diff (System 1)${R}    %b%-8s%b" "$diff_color" "$diff" "$R"
        if [ ${#diff_vals[@]} -gt 1 ]; then
            printf "  "
            sparkline "${diff_vals[@]}"
        fi
        if [ ${#diff_vals[@]} -ge 2 ]; then
            local prev="${diff_vals[-2]}"
            local curr="${diff_vals[-1]}"
            local cmp=$(echo "$curr < $prev" | bc -l 2>/dev/null)
            if [ "$cmp" = "1" ]; then
                printf " ${Fg}↓${R}"
            else
                printf " ${Fr}↑${R}"
            fi
        fi
        printf "\n"

        # Confidence
        printf "  ${D}Confidence Acc${R}     %b%-8s%b" "$Fw" "$conf" "$R"
        if [ "$conf" = "0.0000" ]; then
            printf "  ${Fk}(not learning)${R}"
        elif [ "$(echo "$conf > 0.8" | bc -l 2>/dev/null)" = "1" ]; then
            printf "  ${Fg}good${R}"
        fi
        printf "\n"

        printf "\n  ${D}LR: %s${R}" "$lr"
        if [ "$step" -lt 2000 ]; then
            local lr_pct=$(echo "scale=0; $step * 100 / 2000" | bc 2>/dev/null)
            printf "  ${D}(warmup %s%% → peak 3.0e-04)${R}" "$lr_pct"
        fi
        printf "\n"

        hline
    else
        printf "\n  ${Fy}Waiting for first training step...${R}\n"
        hline
    fi

    # ── Eval ──
    printf "\n"
    printf "  ${B}EVAL METRICS${R}"
    local latest_eval=$(ls -t "$EVAL_DIR"/*.json 2>/dev/null | head -1)
    if [ -n "$latest_eval" ]; then
        local ej=$(cat "$latest_eval")
        local e_step=$(echo "$ej" | python3 -c "import sys,json; print(json.load(sys.stdin)['step'])" 2>/dev/null)
        local e_ppl=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['ar_perplexity']:.0f}\")" 2>/dev/null)
        local e_s1=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['s1_token_accuracy']*100:.2f}\")" 2>/dev/null)
        local e_auroc=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['conf_auroc']:.4f}\")" 2>/dev/null)
        local e_ece=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['conf_ece']:.4f}\")" 2>/dev/null)
        local e_dl=$(echo "$ej" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['diff_loss']:.4f}\")" 2>/dev/null)
        printf "  ${D}@ step %s${R}\n\n" "$e_step"

        printf "  %-22s ${B}%s${R}" "AR Perplexity" "$e_ppl"
        if [ "$e_ppl" -gt 10000 ] 2>/dev/null; then
            printf "   ${Fy}(high — still converging)${R}"
        elif [ "$e_ppl" -lt 100 ] 2>/dev/null; then
            printf "   ${Fg}(strong)${R}"
        fi
        printf "\n"

        printf "  %-22s ${B}%s${R}\n" "Diff Loss" "$e_dl"
        printf "  %-22s ${B}%s%%${R}" "S1 Token Accuracy" "$e_s1"
        local s1_i=$(echo "$e_s1" | cut -d. -f1)
        if [ "$s1_i" -lt 10 ] 2>/dev/null; then
            printf "  ${Fk}(baseline ~2%%, improving)${R}"
        fi
        printf "\n"

        # AUROC gauge
        printf "  %-22s ${B}%s${R}  [" "Conf AUROC" "$e_auroc"
        local auroc_pct=$(echo "$e_auroc * 100" | bc 2>/dev/null | cut -d. -f1)
        local auroc_color="$Fr"
        [ "$auroc_pct" -gt 55 ] && auroc_color="$Fy"
        [ "$auroc_pct" -gt 70 ] && auroc_color="$Fg"
        vbar "$auroc_pct" "$auroc_color"
        printf "] ${D}%.0f%%${R}" "$auroc_pct"
        if [ "$auroc_pct" -lt 55 ] 2>/dev/null; then
            printf "  ${Fk}(~random)${R}"
        fi
        printf "\n"

        printf "  %-22s ${B}%s${R}" "Conf ECE" "$e_ece"
        local ece_i=$(echo "$e_ece * 10000" | bc 2>/dev/null | cut -d. -f1)
        if [ "$ece_i" -lt 100 ] 2>/dev/null; then
            printf "   ${Fg}(well calibrated)${R}"
        fi
        printf "\n"
    else
        printf "  ${D}none yet${R}\n"
    fi

    hline

    # ── GPU ──
    printf "\n"
    printf "  ${B}GPU${R}\n\n"
    local gpu_csv=$(nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,power.limit --format=csv,noheader,nounits 2>/dev/null)
    if [ -n "$gpu_csv" ]; then
        IFS=',' read -r gname gmem_u gmem_t gutil gtemp gpow gpow_max <<< "$gpu_csv"
        gname=$(echo "$gname" | xargs); gmem_u=$(echo "$gmem_u" | xargs)
        gmem_t=$(echo "$gmem_t" | xargs); gutil=$(echo "$gutil" | xargs)
        gtemp=$(echo "$gtemp" | xargs); gpow=$(echo "$gpow" | xargs)
        gpow_max=$(echo "$gpow_max" | xargs)

        printf "  ${D}%-6s${R} ${Fw}%s${R}\n" "Name" "$gname"

        # VRAM bar
        local mem_pct=$((gmem_u * 100 / gmem_t))
        local mem_gb_u=$(echo "scale=1; $gmem_u / 1024" | bc 2>/dev/null)
        local mem_gb_t=$(echo "scale=1; $gmem_t / 1024" | bc 2>/dev/null)
        printf "  ${D}%-6s${R} " "VRAM"
        printf "["
        local mc="$Fg"; [ "$mem_pct" -gt 80 ] && mc="$Fy"; [ "$mem_pct" -gt 90 ] && mc="$Fr"
        vbar "$mem_pct" "$mc"
        printf "] ${B}%s${R}/${D}%s GB${R} (${B}%d%%${R})\n" "$mem_gb_u" "$mem_gb_t" "$mem_pct"

        # Util bar
        printf "  ${D}%-6s${R} " "Util"
        printf "["
        local uc="$Fg"; [ "$gutil" -lt 50 ] && uc="$Fy"; [ "$gutil" -lt 20 ] && uc="$Fr"
        vbar "$gutil" "$uc"
        printf "] ${B}%s%%${R}\n" "$gutil"

        # Temp
        local tc="$Fg"; [ "$gtemp" -gt 75 ] && tc="$Fy"; [ "$gtemp" -gt 85 ] && tc="$Fr"
        printf "  ${D}%-6s${R} %b%s°C%b" "Temp" "$tc" "$gtemp" "$R"

        # Power
        printf "     ${D}Power${R} %sW / %sW\n" "$gpow" "$gpow_max"
    fi

    hline

    # ── Infrastructure ──
    printf "\n"
    printf "  ${B}INFRA${R}\n\n"

    # Trainer
    local tpid=$(pgrep -f joint_trainer 2>/dev/null | head -1)
    if [ -n "$tpid" ]; then
        printf "  Trainer   ${Bg}${B} RUNNING ${R}  ${D}PID %s${R}\n" "$tpid"
    else
        printf "  Trainer   ${Br}${B} STOPPED ${R}\n"
    fi

    # Sync daemon
    local spid=$(pgrep -f sync-checkpoint 2>/dev/null | head -1)
    if [ -n "$spid" ]; then
        printf "  S3 Sync   ${Bg}${B} RUNNING ${R}  ${D}PID %s${R}\n" "$spid"
    else
        printf "  S3 Sync   ${Br}${B} STOPPED ${R}\n"
    fi

    # Checkpoints
    local ck_n=$(ls "$CKPT_DIR"/*.pt 2>/dev/null | wc -l)
    local ck_s=$(du -sh "$CKPT_DIR" 2>/dev/null | cut -f1)
    local next_ckpt=$(( ((step / 5000) + 1) * 5000 ))
    printf "  Ckpts     ${D}%s saved (%s)${R}  ${D}|  next @ step %s${R}\n" "$ck_n" "$ck_s" "$next_ckpt"

    # Next eval
    local next_eval=$(( ((step / 1000) + 1) * 1000 ))
    printf "  Eval      ${D}next @ step %s${R}\n" "$next_eval"

    # W&B
    local wandb_id=$(basename "$(dirname "$(dirname "$WANDB_LOG")")" 2>/dev/null | sed 's/run-[0-9_]*-//')
    if [ -n "$wandb_id" ]; then
        printf "  W&B       ${D}wandb.ai/bitbanshee-c137/dual-process-lm/runs/%s${R}\n" "$wandb_id"
    fi

    printf "\n"
    hline
    printf "\n"
}

trap 'printf "\n"; exit 0' INT TERM
while true; do
    draw
    sleep "$INTERVAL"
done
