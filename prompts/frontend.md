src/
├── theme/                    # design tokens + overrides
│   ├── colors.ts
│   ├── typography.ts
│   └── motion.ts
├── components/               # reusable atoms → molecules → organisms
│   ├── atoms/
│   │   ├── Button.tsx
│   │   ├── Icon.tsx
│   │   └── Spinner.tsx
│   ├── molecules/
│   │   ├── NavBar.tsx
│   │   ├── SideBar.tsx
│   │   └── PanelHeader.tsx
│   ├── organisms/
│   │   ├── DockableLayout.tsx       # drag/drop, resizable panels
│   │   ├── GraphExplorer.tsx        # built with react-flow + deck.gl
│   │   ├── TimeSeriesChart.tsx      # Plotly.js or Recharts
│   │   ├── ComplianceMap.tsx        # deck.gl Choropleth + Sankey
│   │   └── CodeConsole.tsx          # Monaco Editor for query console
│   └── templates/
│       └── WarRoomDashboard.tsx     # composes organisms
├── pages/                       # Next.js pages
│   ├── index.tsx                # redirects to /dashboard
│   ├── dashboard.tsx            # <WarRoomDashboard />
│   └── login.tsx                # Pond-token gated entry
├── hooks/                       # custom hooks (data + ui state)
│   ├── useAuth.ts
│   ├── useWebSocket.ts
│   └── useGraphQL.ts
├── providers/                   # context providers
│   ├── AuthProvider.tsx
│   ├── ThemeProvider.tsx
│   └── LayoutProvider.tsx
├── utils/                       # helpers & constants
├── services/                    # API clients & ws wrappers
│   ├── graphqlClient.ts
│   └── elevenLabs.ts
└── App.tsx                      # root with Chakra & Motion providers 