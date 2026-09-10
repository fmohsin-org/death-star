#!/bin/bash
set -e

echo "=== Sample SAST Findings ==="
npx -y endorctl api list --resource Finding -n auri \
  --filter "spec.finding_categories contains [FINDING_CATEGORY_SAST]" \
  --page-size 5 \
  --field-mask "uuid,meta.name,meta.tags,spec.finding_tags,spec.level,spec.project_uuid"
