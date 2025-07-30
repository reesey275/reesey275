# Pages Deployer Agent

scope: website
role: maintainer

This agent builds a static site from `index.md` or the `docs/` directory and
publishes the result to GitHub Pages. The generated files should be placed in a
`public/` folder so the `deploy-pages` workflow can upload and deploy them.
