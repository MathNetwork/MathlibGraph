export default {
  logo: <span style={{ fontWeight: 700, fontSize: '1.5rem' }}>MathlibGraph</span>,
  project: {
    link: 'https://github.com/MathNetwork/MathlibGraph',
  },
  docsRepositoryBase: 'https://github.com/MathNetwork/MathlibGraph/tree/main/docs',
  footer: {
    component: null,
  },
  gitTimestamp: ({ timestamp }) => (
    <span style={{ fontSize: '0.75rem', color: '#888' }}>
      Last updated on {timestamp.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
      {' · '}Apache 2.0 © 2026 MathNetwork
    </span>
  ),
  feedback: {
    content: null,
  },
  editLink: {
    component: null,
  },
  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="description" content="MathlibGraph - Network analysis of Mathlib4 dependency structure" />
      <title>MathlibGraph</title>
    </>
  ),
  darkMode: true,
  nextThemes: {
    defaultTheme: 'dark',
    forcedTheme: 'dark',
  },
  sidebar: {
    toggleButton: true,
  },
  toc: {
    backToTop: true,
  },
  navigation: false,
}
