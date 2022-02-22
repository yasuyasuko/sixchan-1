(function () {
  Set.prototype.union = function (other) {
    const _union = new Set([...this]);
    for (let elem of other) {
      _union.add(elem);
    }
    return _union;
  };

  Set.prototype.pop = function () {
    const top = Array.from(this).shift();
    this.delete(top);
    return top;
  };

  const solveRefs = directRefs => {
    const refs = directRefs.map(_ => new Set());
    for (let n = 1; n < refs.length; n++) {
      let nexts = new Set([...directRefs[n]]);
      const visited = new Set();
      while (nexts.size) {
        const next = nexts.pop();
        if ((next === n) | visited.has(next)) 
          continue;
        refs[n].add(next);
        refs[next].add(n);
        visited.add(next);
        nexts = nexts.union(directRefs[next]);
      }
    }
    return refs;
  };

  const generateDirectRefs = () => {
    const re = />>(?<id>[1-9]|[1-9][0-9]{1,2}|1000)/gm;
    const iter = document.evaluate("//div[@id='res-container']/div", document, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);
    const directRefs = [new Set()];
    let res = null;
    while ((res = iter.iterateNext())) {
      const id = Math.trunc(res.getAttribute("id"));
      const body = document.getElementById(`${id}-body`);
      const matches = body.innerText.matchAll(re);
      directRefs.push(new Set(Array.from(matches).map(m => Math.trunc(m.groups.id))));
    }
    return directRefs;
  };

  const replaceAngleToAnchor = () => {
    const re = /(?<angle>&gt;&gt;)(?<num>[1-9]|[1-9][0-9]{1,2}|1000)/gm;
    const bodies = document.querySelectorAll("[id$='-body']");
    bodies.forEach(body => {
      const a = '<a href="#$<id>" class="text-blue-500 hover:text-blue-400">$<angle>$<num></a>';
      body.innerHTML = body.innerHTML.replace(re, a);
    });
  };

  const setupButton = (num, ref) => {
    const resContainer = document.getElementById(`${num}`);
    const actionContainer = document.getElementById(`${num}-action`);
    const refContainer = document.createElement("div");
    const button = document.createElement("button");
    button.classList.add("mr-1", "text-gray-400", "text-xs", "hover:underline");
    button.innerText = "関連レスを表示";
    button.onclick = () => showRef(refContainer, num, ref);
    actionContainer.prepend(button);
    resContainer.appendChild(refContainer);
  };

  const showRef = (resContainer, num, ref) => {
    const existed = document.getElementById(`${num}-ref`);
    if (existed) {
      resContainer.removeChild(existed);
    } else {
      const refDisplayArea = document.createElement("div");
      refDisplayArea.setAttribute("id", `${num}-ref`);
      refDisplayArea.classList.add("mt-1", "border-t-2");
      for (targetNum of Array.from(ref).sort()) {
        const original = document.getElementById(`${targetNum}`);
        const cloned = original.cloneNode(true);
        cloned.classList.add("shadow");
        const buttons = cloned.getElementsByTagName("button");
        if (buttons) {
          const parent = buttons[0].parentElement;
          cloned.removeChild(parent);
        }
        refDisplayArea.appendChild(cloned);
      }
      resContainer.appendChild(refDisplayArea);
    }
  };

  const initialize = () => {
    replaceAngleToAnchor();
    const refs = solveRefs(generateDirectRefs());
    refs.forEach((ref, num) => {
      if ((num === 0) | (ref.size === 0)) 
        return;
      setupButton(num, ref);
    });
  };

  // entry point
  initialize();
})();
