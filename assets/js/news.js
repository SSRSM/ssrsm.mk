const newsPost = ({ imgSrc, title, id, text, date }) =>
	`<div class="col-md-6 d-flex align-items-stretch">
	<div class="card">
		<div class="card-img">
			<img src="${imgSrc}">
		</div>
		<div class="card-body">
			<h5 class="card-title"><a href="/news/post.html?id=${id}">${title}</a></h5>
			<p class="fst-italic text-center">${new Date(date).toUTCString()}</p>
			<p class="card-text">${text}</p>
		</div>
	</div>
</div>`;

(async () => {
	const res = await fetch('/news/index.json');
	const newsIndex = await res.json();

	console.log(newsIndex);

	newsIndex.forEach(async ({ id }) => {
		const res = await fetch(`/news/${id}.json`);
		const post = await res.json();

		console.log({ id, ...post });

		document.querySelector('#news .row').innerHTML += newsPost({ id, ...post });
	});
})();