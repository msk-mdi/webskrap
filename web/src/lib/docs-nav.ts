export interface NavItem {
  title: string;
  href: string;
}

export interface NavSection {
  title?: string;
  items: NavItem[];
}

export const NAV: NavSection[] = [
  { items: [{ title: "Home", href: "/docs" }] },
  {
    title: "Getting Started",
    items: [
      { title: "Installation", href: "/docs/getting-started/installation" },
      { title: "Quickstart", href: "/docs/getting-started/quickstart" },
    ],
  },
  {
    title: "User Guide",
    items: [
      { title: "Client", href: "/docs/user-guide/client" },
      { title: "Sessions", href: "/docs/user-guide/sessions" },
      { title: "Profiles", href: "/docs/user-guide/profiles" },
      { title: "Stealth", href: "/docs/user-guide/stealth" },
      { title: "Resource Policy", href: "/docs/user-guide/resource-policy" },
      { title: "CLI", href: "/docs/user-guide/cli" },
      { title: "MCP Server", href: "/docs/user-guide/mcp" },
    ],
  },
  {
    title: "Reference",
    items: [
      { title: "API Reference", href: "/docs/api-reference" },
      { title: "Development", href: "/docs/development" },
    ],
  },
];

// Every doc slug derived from the nav (["/docs"] -> []).
export function getDocSlugs(): string[][] {
  return NAV.flatMap((section) =>
    section.items.map((item) =>
      item.href.replace(/^\/docs\/?/, "").split("/").filter(Boolean),
    ),
  );
}
