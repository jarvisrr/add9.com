(function () {
  "use strict";

  var audioCtx = null;
  var activeProgTimers = [];
  var activeProgBtn = null;

  function getCtx() {
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    if (!audioCtx) audioCtx = new AC();
    if (audioCtx.state === "suspended") audioCtx.resume();
    return audioCtx;
  }

  function midiToFreq(midi) {
    return 440 * Math.pow(2, (midi - 69) / 12);
  }

  function parseMidis(raw) {
    return (raw || "")
      .split(",")
      .map(function (n) {
        return parseInt(n, 10);
      })
      .filter(function (n) {
        return !isNaN(n);
      });
  }

  function pluckNote(ctx, freq, startTime, duration) {
    var osc1 = ctx.createOscillator();
    var osc2 = ctx.createOscillator();
    var filter = ctx.createBiquadFilter();
    var gain = ctx.createGain();

    osc1.type = "triangle";
    osc1.frequency.setValueAtTime(freq, startTime);

    osc2.type = "sine";
    osc2.frequency.setValueAtTime(freq * 2, startTime);

    filter.type = "lowpass";
    filter.frequency.setValueAtTime(Math.min(4200, freq * 7), startTime);
    filter.frequency.exponentialRampToValueAtTime(Math.max(420, freq * 1.8), startTime + duration);

    gain.gain.setValueAtTime(0.0001, startTime);
    gain.gain.linearRampToValueAtTime(0.16, startTime + 0.012);
    gain.gain.exponentialRampToValueAtTime(0.0008, startTime + duration);

    var harmGain = ctx.createGain();
    harmGain.gain.setValueAtTime(0.28, startTime);

    osc1.connect(filter);
    osc2.connect(harmGain);
    harmGain.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);

    osc1.start(startTime);
    osc2.start(startTime);
    osc1.stop(startTime + duration + 0.05);
    osc2.stop(startTime + duration + 0.05);
  }

  function strumMidiList(midis, button) {
    var ctx = getCtx();
    if (!ctx || !midis.length) return;
    var now = ctx.currentTime + 0.02;
    midis.forEach(function (midi, idx) {
      pluckNote(ctx, midiToFreq(midi), now + idx * 0.036, 1.9);
    });
    if (button) {
      button.classList.add("is-playing");
      window.setTimeout(function () {
        button.classList.remove("is-playing");
      }, 650);
    }
  }

  function clearProgTimers() {
    activeProgTimers.forEach(function (id) {
      window.clearTimeout(id);
    });
    activeProgTimers = [];
    document.querySelectorAll(".prog-step.is-active").forEach(function (el) {
      el.classList.remove("is-active");
    });
    if (activeProgBtn) {
      activeProgBtn.classList.remove("is-playing");
      activeProgBtn.setAttribute("aria-pressed", "false");
      var lbl = activeProgBtn.querySelector("span");
      var defText = activeProgBtn.getAttribute("data-label-play");
      if (lbl && defText) lbl.textContent = defText;
      activeProgBtn = null;
    }
  }

  function setShowcaseIndex(root, idx) {
    var imgs = root.querySelectorAll("[data-screen-img]");
    var count = imgs.length;
    if (!count) return;
    var next = ((idx % count) + count) % count;
    root.setAttribute("data-active-idx", String(next));
    imgs.forEach(function (img, i) {
      img.classList.toggle("is-active", i === next);
    });
    root.querySelectorAll("[data-screen-tab]").forEach(function (t, i) {
      t.setAttribute("aria-selected", i === next ? "true" : "false");
    });
    root.querySelectorAll("[data-screen-dot]").forEach(function (d, i) {
      d.setAttribute("aria-pressed", i === next ? "true" : "false");
    });
  }

  document.addEventListener("click", function (ev) {
    var sTab = ev.target.closest("[data-screen-tab], [data-screen-dot]");
    if (sTab) {
      var showcase = sTab.closest(".showcase");
      if (!showcase) return;
      var val = sTab.getAttribute("data-screen-tab") || sTab.getAttribute("data-screen-dot");
      setShowcaseIndex(showcase, parseInt(val, 10) || 0);
      return;
    }

    var screenBox = ev.target.closest(".iphone-screen");
    if (screenBox) {
      var sc = screenBox.closest(".showcase");
      if (!sc) return;
      var cur = parseInt(sc.getAttribute("data-active-idx") || "0", 10);
      setShowcaseIndex(sc, cur + 1);
      return;
    }

    var progBtn = ev.target.closest("[data-play-progression]");
    if (progBtn) {
      var panel = progBtn.closest(".guide-panel");
      if (!panel) return;
      if (activeProgBtn === progBtn) {
        clearProgTimers();
        return;
      }
      clearProgTimers();
      var steps = Array.prototype.slice.call(panel.querySelectorAll(".prog-step[data-midi]"));
      activeProgBtn = progBtn;
      progBtn.classList.add("is-playing");
      progBtn.setAttribute("aria-pressed", "true");
      var lbl = progBtn.querySelector("span");
      var stopText = progBtn.getAttribute("data-label-stop");
      if (lbl && stopText) lbl.textContent = stopText;
      steps.forEach(function (step, i) {
        var id = window.setTimeout(function () {
          steps.forEach(function (s) {
            s.classList.toggle("is-active", s === step);
          });
          strumMidiList(parseMidis(step.getAttribute("data-midi")), null);
        }, i * 1150);
        activeProgTimers.push(id);
      });
      var endId = window.setTimeout(function () {
        clearProgTimers();
      }, steps.length * 1150 + 400);
      activeProgTimers.push(endId);
      return;
    }

    var btn = ev.target.closest("[data-midi]");
    if (btn) {
      strumMidiList(parseMidis(btn.getAttribute("data-midi")), btn);
      return;
    }

    var tab = ev.target.closest("[data-bench-idx]");
    if (tab) {
      var bench = tab.closest(".bench");
      if (!bench) return;
      var idx = tab.getAttribute("data-bench-idx");
      bench.querySelectorAll("[data-bench-idx]").forEach(function (t) {
        t.setAttribute("aria-pressed", t === tab ? "true" : "false");
      });
      bench.querySelectorAll("[data-bench-panel]").forEach(function (p) {
        var match = p.getAttribute("data-bench-panel") === idx;
        p.hidden = !match;
        if (match) {
          var playBtn = p.querySelector("[data-midi]");
          if (playBtn) {
            strumMidiList(parseMidis(playBtn.getAttribute("data-midi")), playBtn);
          }
        }
      });
    }
  });

  document.addEventListener("keydown", function (ev) {
    var sTab = ev.target.closest("[data-screen-tab]");
    if (!sTab) return;
    if (ev.key !== "ArrowDown" && ev.key !== "ArrowUp" && ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
    var showcase = sTab.closest(".showcase");
    if (!showcase) return;
    ev.preventDefault();
    var cur = parseInt(sTab.getAttribute("data-screen-tab") || "0", 10);
    var delta = ev.key === "ArrowDown" || ev.key === "ArrowRight" ? 1 : -1;
    setShowcaseIndex(showcase, cur + delta);
    var nextIdx = parseInt(showcase.getAttribute("data-active-idx") || "0", 10);
    var nextBtn = showcase.querySelector('[data-screen-tab="' + nextIdx + '"]');
    if (nextBtn) nextBtn.focus();
  });
})();
