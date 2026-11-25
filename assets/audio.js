(function () {
  "use strict";

  var audioCtx = null;
  var activeProgTimers = [];

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
  }

  document.addEventListener("click", function (ev) {
    var progBtn = ev.target.closest("[data-play-progression]");
    if (progBtn) {
      var panel = progBtn.closest(".guide-panel");
      if (!panel) return;
      clearProgTimers();
      var steps = Array.prototype.slice.call(panel.querySelectorAll(".prog-step[data-midi]"));
      progBtn.classList.add("is-playing");
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
        progBtn.classList.remove("is-playing");
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
})();
