// Content remains visible when scripts or motion are unavailable.
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
if ("IntersectionObserver" in window && !reduceMotion.matches) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add("motion-visible");
        observer.unobserve(entry.target);
      }
    }
  }, { threshold: 0.12 });

  document.querySelectorAll(".results-copy h2, .method h2, .reproduce h2, .results .chart")
    .forEach(element => {
      element.classList.add("motion-ready");
      observer.observe(element);
    });
}
