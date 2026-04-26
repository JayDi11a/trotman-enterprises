#!/bin/bash
# Live deployment status dashboard for distributed ML infrastructure

CONTROL="192.168.1.130"
WORKER="192.168.1.131"
PASS="Pass4Admin"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

clear
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}        ML Model Deployment Status - Distributed Architecture${NC}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "$(date '+%A, %B %d, %Y - %H:%M:%S %Z')"
echo ""

# ============================================
# CONTROL NODE STATUS (192.168.1.130)
# ============================================
echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║ CONTROL NODE (192.168.1.130) - Small Models + LiteLLM Proxy         ║${NC}"
echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Memory status
echo -e "${YELLOW}Memory Status:${NC}"
ssh root@$CONTROL "free -h | grep -E 'Mem|Swap' | awk '{printf \"  %-8s %8s total  %8s used  %8s free  %8s available\n\", \$1, \$2, \$3, \$4, \$7}'"
echo ""

# Running services
echo -e "${YELLOW}Running Model Services:${NC}"
ssh root@$CONTROL "systemctl list-units 'llama-cpp-*.service' --no-pager --no-legend 2>/dev/null | awk '{
    status = (\$4 == \"running\") ? \"✓\" : \"✗\";
    color = (\$4 == \"running\") ? \"${GREEN}\" : \"${RED}\";
    printf \"  %s%s${NC} %-40s %s\n\", color, status, \$1, \$4
}' || echo '  No services running'"
echo ""

# LiteLLM proxy
echo -e "${YELLOW}LiteLLM Proxy:${NC}"
LITELLM_STATUS=$(ssh root@$CONTROL "systemctl is-active litellm-proxy.service 2>/dev/null || echo 'inactive'")
if [ "$LITELLM_STATUS" = "active" ]; then
    echo -e "  ${GREEN}✓${NC} Running on port 4000"
    HEALTH=$(ssh root@$CONTROL "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:4000/health 2>/dev/null || echo '000'")
    if [ "$HEALTH" = "200" ] || [ "$HEALTH" = "401" ]; then
        echo -e "  ${GREEN}✓${NC} API responding (HTTP $HEALTH)"
    else
        echo -e "  ${RED}✗${NC} API not responding (HTTP $HEALTH)"
    fi
else
    echo -e "  ${RED}✗${NC} Not running"
fi
echo ""

# Active downloads
echo -e "${YELLOW}Active Downloads:${NC}"
DOWNLOAD_COUNT=$(ssh root@$CONTROL "ps aux | grep 'hf download' | grep -v grep | wc -l")
if [ "$DOWNLOAD_COUNT" -gt 0 ]; then
    echo -e "  ${BLUE}↓${NC} $DOWNLOAD_COUNT HuggingFace downloads in progress"
    ssh root@$CONTROL "du -sh /models/qwen2.5-32b /models/qwen2.5-72b /models/mixtral-8x7b /models/mixtral-8x22b 2>/dev/null | awk '{
        split(\$2, path, \"/\");
        model = path[3];
        size = \$1;

        # Expected sizes
        if (model == \"qwen2.5-32b\") expected = \"19G\";
        else if (model == \"qwen2.5-72b\") expected = \"43G\";
        else if (model == \"mixtral-8x7b\") expected = \"26G\";
        else if (model == \"mixtral-8x22b\") expected = \"87G\";

        # Calculate percentage (rough)
        gsub(/G/, \"\", size);
        gsub(/G/, \"\", expected);
        pct = int((size / expected) * 100);

        bar = \"\";
        for (i=0; i<pct/5; i++) bar = bar \"█\";
        for (i=pct/5; i<20; i++) bar = bar \"░\";

        printf \"    %-20s [%s] %3d%% (%sG/%s)\n\", model, bar, pct, \$1, expected;
    }'"
else
    echo -e "  ${GREEN}✓${NC} All downloads complete"
fi
echo ""

# ============================================
# WORKER NODE STATUS (192.168.1.131)
# ============================================
echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║ WORKER NODE (192.168.1.131) - Large Models                          ║${NC}"
echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Memory status
echo -e "${YELLOW}Memory Status:${NC}"
sshpass -p "$PASS" ssh root@$WORKER "free -h | grep -E 'Mem|Swap' | awk '{printf \"  %-8s %8s total  %8s used  %8s free  %8s available\n\", \$1, \$2, \$3, \$4, \$7}'"
echo ""

# Running services
echo -e "${YELLOW}Running Model Services:${NC}"
WORKER_SERVICES=$(sshpass -p "$PASS" ssh root@$WORKER "systemctl list-units 'llama-cpp-*.service' --no-pager --no-legend 2>/dev/null | wc -l")
if [ "$WORKER_SERVICES" -gt 0 ]; then
    sshpass -p "$PASS" ssh root@$WORKER "systemctl list-units 'llama-cpp-*.service' --no-pager --no-legend 2>/dev/null | awk '{
        status = (\$4 == \"running\") ? \"✓\" : \"✗\";
        color = (\$4 == \"running\") ? \"${GREEN}\" : \"${RED}\";
        printf \"  %s%s${NC} %-40s %s\n\", color, status, \$1, \$4
    }'"
else
    echo -e "  ${BLUE}○${NC} No services deployed yet (waiting for model copies)"
fi
echo ""

# Active file copies
echo -e "${YELLOW}Active File Transfers:${NC}"
RSYNC_ACTIVE=$(ssh root@$CONTROL "ps aux | grep 'rsync.*192.168.1.131' | grep -v grep | wc -l")
if [ "$RSYNC_ACTIVE" -gt 0 ]; then
    echo -e "  ${BLUE}↑${NC} Rsync transfer in progress:"

    # Check Llama 70B copy
    if ssh root@$CONTROL "ps aux | grep 'rsync.*llama-3.1-70b' | grep -v grep" > /dev/null 2>&1; then
        # Get current size on worker
        CURRENT=$(sshpass -p "$PASS" ssh root@$WORKER "du -s /models/llama-3.1-70b 2>/dev/null | awk '{print \$1}'" || echo "0")
        TOTAL=41943040  # 40GB in KB

        if [ "$CURRENT" -gt 0 ]; then
            PCT=$((CURRENT * 100 / TOTAL))
            CURRENT_GB=$((CURRENT / 1024 / 1024))

            bar=""
            for ((i=0; i<PCT/5; i++)); do bar="${bar}█"; done
            for ((i=PCT/5; i<20; i++)); do bar="${bar}░"; done

            echo -e "    Llama 3.1 70B        [${bar}] ${PCT}% (${CURRENT_GB}GB/40GB)"

            # Show latest log line for speed
            LAST_LINE=$(ssh root@$CONTROL "tail -1 /tmp/rsync-llama70b.log 2>/dev/null | grep -oP '\d+\.\d+MB/s' | tail -1" || echo "calculating...")
            echo -e "      Transfer rate: $LAST_LINE"
        else
            echo -e "    Llama 3.1 70B        [${BLUE}starting...${NC}]"
        fi
    fi
else
    echo -e "  ${GREEN}✓${NC} No active transfers"
fi
echo ""

# ============================================
# DEPLOYMENT SUMMARY
# ============================================
echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║ DEPLOYMENT SUMMARY                                                   ║${NC}"
echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Count deployed models
CONTROL_MODELS=$(ssh root@$CONTROL "systemctl list-units 'llama-cpp-*.service' --state=running --no-pager --no-legend 2>/dev/null | wc -l")
WORKER_MODELS=$(sshpass -p "$PASS" ssh root@$WORKER "systemctl list-units 'llama-cpp-*.service' --state=running --no-pager --no-legend 2>/dev/null | wc -l")
TOTAL_MODELS=$((CONTROL_MODELS + WORKER_MODELS))

echo -e "  ${BOLD}Local Models:${NC}"
echo -e "    Control node: ${GREEN}${CONTROL_MODELS}${NC} running"
echo -e "    Worker node:  ${GREEN}${WORKER_MODELS}${NC} running"
echo -e "    ${BOLD}Total:        ${GREEN}${TOTAL_MODELS}/10${NC} local models deployed${NC}"
echo ""

# Target architecture
echo -e "  ${BOLD}Target Architecture:${NC}"
echo -e "    Control: 5 small/medium models (Hermes 8B, Qwen 14B, Granite 8B, Functionary, Qwen 32B)"
echo -e "    Worker:  4 large models (Llama 70B, Qwen 72B, Mixtral 8x7B, Mixtral 8x22B)"
echo -e "    Cloud:   5 cloud models (Claude, GPT-4o, Gemini)"
echo -e "    ${BOLD}Total:   15 models accessible via LiteLLM${NC}"
echo ""

# Next steps
echo -e "  ${BOLD}Next Steps:${NC}"
if [ "$RSYNC_ACTIVE" -gt 0 ]; then
    echo -e "    ${BLUE}•${NC} Waiting for Llama 70B copy to complete (~50 min remaining)"
fi
if [ "$DOWNLOAD_COUNT" -gt 0 ]; then
    echo -e "    ${BLUE}•${NC} Downloading remaining models on control node"
fi
if [ "$WORKER_MODELS" -eq 0 ]; then
    echo -e "    ${BLUE}•${NC} Deploy large model services on worker when copies complete"
fi
if [ "$TOTAL_MODELS" -lt 10 ]; then
    echo -e "    ${BLUE}•${NC} Update LiteLLM config to route to worker endpoints"
fi
echo ""

echo -e "${BOLD}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}Refresh: watch -n 30 ./scripts/deployment-status.sh${NC}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════════${NC}"
