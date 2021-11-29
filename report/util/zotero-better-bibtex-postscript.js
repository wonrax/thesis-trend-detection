if (Translator.BetterBibTeX) {
    if (reference.has.howpublished) {
        reference.remove("howpublished");
    }

    if (item.url) {
      reference.add({ name: 'url', value: item.url });
    }

    if (item.accessDate) {
        reference.add({ name: 'note', value: "Truy cập lần cuối " + item.accessDate.replace(/\s*T?\d+:\d+:\d+.*/, '') });
	}
}