#!/bin/bash
set -e

echo "=== Projects in auri namespace ==="
npx -y endorctl api list --resource Project -n auri --field-mask "meta.name,uuid" 2>/dev/null || echo "FAILED: could not list projects"

echo ""
echo "=== SAST Findings Count ==="
npx -y endorctl api list --resource Finding -n auri \
  --filter "spec.finding_categories contains [FINDING_CATEGORY_SAST]" \
  --count 2>/dev/null || echo "FAILED: could not count SAST findings"

echo ""
echo "=== Sample 3 SAST Findings ==="
npx -y endorctl api list --resource Finding -n auri \
  --filter "spec.finding_categories contains [FINDING_CATEGORY_SAST]" \
  --page-size 3 \
  --field-mask "uuid,meta.name,meta.description,meta.tags,spec.finding_tags,spec.level" 2>/dev/null || echo "FAILED: could not list SAST findings"
