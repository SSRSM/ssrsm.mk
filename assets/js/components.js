(async function () {
	await Promise.all([...document.querySelectorAll('component')].map(async (component) => {
		const reqUrl = component.getAttribute('src');

		if (!reqUrl) return;

		const res = await fetch(reqUrl);
		const resHtml = await res.text();

		const proppedHtml = resHtml.replace(/-{-.*-}-/g, (match) => {
			return component.getAttribute(`data-${match.match(/(?<=-{-).*(?=-}-)/)[0]}`);
		});

		component.outerHTML = proppedHtml;
	}));

	const scriptTag = document.createElement('script');

	scriptTag.setAttribute('src', 'assets/vendor/purecounter/purecounter.js');

	document.head.appendChild(scriptTag);
})()