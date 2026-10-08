# SCI UI

Local workspace package used by the dashboard, desktop and native bootstrap UI.
Its reviewed components and styles are included in the checkout; installation
does not fetch a publisher's design-system package. Import individual components
from `@sci/ui/ui/components/...`, hooks from `@sci/ui/hooks/...`, and the
`@sci/ui/styles/fonts.css` and `globals.css` stylesheets.

The initial component subset derives from the MIT-licensed
`@nous-research/ui` version 0.18.2. Only components used by SCI and their
dependencies are included. Publisher artwork, testimonials, demonstrations and
unused components are excluded. Original attribution is retained in LICENSE.

The checked-in JavaScript and declarations are runtime source for this package,
not a local build cache. Keep them in Git. React and shared dependencies are
resolved by the repository's root npm workspace lockfile.
