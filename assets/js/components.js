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

	const scripts = [
		'assets/vendor/purecounter/purecounter.js',
		'assets/js/afterComponents.js'
	]

	for (const scriptUrl of scripts) {
		const scriptTag = document.createElement('script');

		scriptTag.setAttribute('src', scriptUrl);

		document.head.appendChild(scriptTag);
	}
})()