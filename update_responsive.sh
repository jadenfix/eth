#!/bin/bash

# Update remaining pages to use ResponsiveLayout
PAGES=("analytics.tsx" "workspace.tsx")

for page in "${PAGES[@]}"; do
    echo "Updating $page..."
    
    # Add ResponsiveLayout import
    sed -i '' 's|from '\''../src/components'\'';|from '\''../src/components'\'';|g' "/Users/jadenfix/eth/services/ui/nextjs-app/pages/$page"
    sed -i '' 's|} from '\''@chakra-ui/react'\'';|} from '\''@chakra-ui/react'\'';\nimport { ResponsiveLayout } from '\''../src/components'\'';|g' "/Users/jadenfix/eth/services/ui/nextjs-app/pages/$page"
    
    echo "Updated $page"
done

echo "All pages updated!"
