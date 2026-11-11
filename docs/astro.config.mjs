// @ts-check
// The shared max-models docs setup (@max-models/starlight-theme): served at
// https://max-models.github.io/plasma-presentations/, with math, the API reference and a link check.
import { defineDocs } from '@max-models/starlight-theme';

export default defineDocs({
	repo: 'plasma-presentations',
	title: 'plasma-presentations',
	description: 'Talks written as Quarto slides with the max-models look: HTML with reveal.js and PDF with Beamer.',
	pythonPackage: 'plasma_presentations',
	nav: [
		{ label: 'Getting started', link: '/getting-started/installation/' },
		{ label: 'Examples', link: '/examples/' },
		{ label: 'Development', link: '/development/docs/' },
		{ label: 'API', link: '/api/plasma_presentations/' },
	],
	sidebar: [
		{
			label: 'Getting started',
			items: [
				{ label: 'Installation', slug: 'getting-started/installation' },
				{ label: 'Quickstart', slug: 'getting-started/quickstart' },
			],
		},
		{
			label: 'Examples',
			items: [
				{ autogenerate: { directory: 'examples' } },
				{ label: 'Scripts', items: [{ autogenerate: { directory: 'example-scripts' } }] },
			],
		},
		{
			label: 'Development',
			items: [
				{ label: 'Building the docs', slug: 'development/docs' },
				{ label: 'Publishing', slug: 'development/publishing' },
			],
		},
	],
});
