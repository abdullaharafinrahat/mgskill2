// beats.js — word timing helper (sampled from repo, trimmed)
(function(){
  window.Beats = {
    // simple linear per-word map; real build uses words.py -> beats.json
    fromPlan: (words, duration) => {
      const per = duration/words.length;
      return words.map((w,i)=>({w, t:i*per}));
    },
    hitTimes: (beats, re) => beats.filter(b=>re.test(b.w)).map(b=>b.t)
  };
})();
