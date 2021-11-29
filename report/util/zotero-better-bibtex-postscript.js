if (Translator.BetterBibTeX) {
    if (reference.has.howpublished) {
        reference.remove("howpublished");
    }
    if (item.url) {
      reference.add({ name: 'url', value: item.url });
    }
}