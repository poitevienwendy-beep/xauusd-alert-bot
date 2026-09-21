/*!
 * muscle-map — schéma musculaire interactif pour l'app d'entraînement.
 *
 * Sans dépendance. Charge assets/figures.js avant ce fichier, ou passe les
 * SVG à la main via l'option `figures`.
 *
 *   <script src="assets/figures.js"></script>
 *   <script src="muscle-map.js"></script>
 *   <script>
 *     const map = MuscleMap.mount('#schema', { view: 'both' });
 *     map.set({ chest: 'primary', shoulders: 'secondary', triceps: 'secondary' });
 *   </script>
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.MuscleMap = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var VIEWS = ['front', 'back'];

  // Chaque montage renumérote les id internes des SVG (dégradés, masque de
  // découpe). Sans ça, deux figures de la même vue sur une même page
  // partageraient les mêmes id : la seconde irait chercher les dégradés de la
  // première et hériterait de son thème.
  var instances = 0;

  // Intensité de sollicitation. 0 = au repos, 3 = muscle principal.
  var LEVELS = {
    none: 0, off: 0, repos: 0,
    light: 1, stabilizer: 1, secondaire: 1,
    medium: 2, secondary: 2, synergiste: 2,
    heavy: 3, primary: 3, principal: 3
  };

  function toLevel(value) {
    if (value == null || value === false) return 0;
    if (value === true) return 3;
    if (typeof value === 'string') {
      var named = LEVELS[value.toLowerCase()];
      return named == null ? 0 : named;
    }
    var n = Math.round(Number(value));
    if (!isFinite(n) || n < 0) return 0;
    return n > 3 ? 3 : n;
  }

  function resolveElement(target) {
    var el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) throw new Error('MuscleMap : cible introuvable (' + target + ')');
    return el;
  }

  function MuscleMap(target, options) {
    options = options || {};
    var figures = options.figures ||
      (typeof MuscleMapFigures !== 'undefined' ? MuscleMapFigures.figures : null);
    if (!figures) {
      throw new Error('MuscleMap : figures manquantes — charge assets/figures.js d’abord.');
    }

    this.labels = options.labels ||
      (typeof MuscleMapFigures !== 'undefined' ? MuscleMapFigures.labels : {}) || {};
    this._figures = figures;
    this._root = resolveElement(target);
    this._levels = {};
    this._listeners = { select: [], change: [] };
    this._interactive = options.interactive !== false;
    this._uid = ++instances;
    // Sur clic : parcours des intensités proposées. [0, 3] = simple bascule.
    this._cycle = (options.cycle || [0, 3]).map(toLevel);
    this._view = null;

    this._onClick = this._onClick.bind(this);
    this._onKeyDown = this._onKeyDown.bind(this);

    this.setView(options.view || 'front');
    if (options.levels) this.set(options.levels);
    if (typeof options.onSelect === 'function') this.on('select', options.onSelect);
    if (typeof options.onChange === 'function') this.on('change', options.onChange);
  }

  MuscleMap.prototype = {

    /** 'front', 'back' ou 'both'. */
    setView: function (view) {
      if (view !== 'both' && VIEWS.indexOf(view) === -1) {
        throw new Error('MuscleMap : vue inconnue « ' + view + ' »');
      }
      if (view === this._view) return this;
      this._view = view;

      var wanted = view === 'both' ? VIEWS : [view];
      this._root.classList.add('mm-root');
      this._root.setAttribute('data-view', view);
      this._root.innerHTML = wanted.map(function (v) {
        return this._scopeIds(this._figures[v]);
      }, this).join('');

      this._figuresEls = Array.prototype.slice.call(this._root.querySelectorAll('.mm-figure'));
      this._figuresEls.forEach(function (svg) {
        svg.setAttribute('data-interactive', String(this._interactive));
        svg.addEventListener('click', this._onClick);
        svg.addEventListener('keydown', this._onKeyDown);
        if (this._interactive) {
          svg.querySelectorAll('.mm-muscle').forEach(function (g) {
            g.setAttribute('tabindex', '0');
          });
        }
      }, this);

      this._paint();
      return this;
    },

    getView: function () { return this._view; },

    /** Remplace entièrement la sollicitation affichée. */
    set: function (levels) {
      this._levels = {};
      return this.update(levels || {});
    },

    /** Fusionne avec l'état courant. */
    update: function (levels) {
      Object.keys(levels || {}).forEach(function (key) {
        var lvl = toLevel(levels[key]);
        if (lvl === 0) delete this._levels[key];
        else this._levels[key] = lvl;
      }, this);
      this._paint();
      this._emit('change', { levels: this.get() });
      return this;
    },

    clear: function () { return this.set({}); },

    /** Copie de l'état : { chest: 3, triceps: 2 }. */
    get: function () {
      var levels = this._levels;
      var out = {};
      Object.keys(levels).forEach(function (k) { out[k] = levels[k]; });
      return out;
    },

    levelOf: function (muscle) { return this._levels[muscle] || 0; },

    /** Clés présentes dans la ou les vues affichées. */
    muscles: function () {
      var seen = {};
      this._figuresEls.forEach(function (svg) {
        svg.querySelectorAll('.mm-muscle').forEach(function (g) {
          seen[g.getAttribute('data-muscle')] = true;
        });
      });
      return Object.keys(seen);
    },

    on: function (event, handler) {
      if (this._listeners[event]) this._listeners[event].push(handler);
      return this;
    },

    off: function (event, handler) {
      var list = this._listeners[event];
      if (!list) return this;
      var i = list.indexOf(handler);
      if (i !== -1) list.splice(i, 1);
      return this;
    },

    destroy: function () {
      this._figuresEls.forEach(function (svg) {
        svg.removeEventListener('click', this._onClick);
        svg.removeEventListener('keydown', this._onKeyDown);
      }, this);
      this._root.innerHTML = '';
      this._root.removeAttribute('data-view');
      this._listeners = { select: [], change: [] };
    },

    // --- interne ---------------------------------------------------------

    /** Préfixe les id internes d'un SVG pour isoler cette instance. */
    _scopeIds: function (svg) {
      var prefix = 'mm-i' + this._uid + '-';
      return svg.replace(/id="mm-/g, 'id="' + prefix)
                .replace(/url\(#mm-/g, 'url(#' + prefix);
    },

    _paint: function () {
      this._figuresEls.forEach(function (svg) {
        svg.querySelectorAll('.mm-muscle').forEach(function (g) {
          var key = g.getAttribute('data-muscle');
          var lvl = this._levels[key] || 0;
          g.setAttribute('data-level', String(lvl));
          g.setAttribute('aria-pressed', String(lvl > 0));
        }, this);
      }, this);
    },

    _emit: function (event, payload) {
      (this._listeners[event] || []).forEach(function (fn) { fn(payload); });
    },

    _nextLevel: function (current) {
      var i = this._cycle.indexOf(current);
      return this._cycle[(i + 1) % this._cycle.length];
    },

    _activate: function (group) {
      var key = group.getAttribute('data-muscle');
      var previous = this._levels[key] || 0;
      var next = this._interactive ? this._nextLevel(previous) : previous;
      if (this._interactive) {
        this.update((function (o) { o[key] = next; return o; })({}));
      }
      this._emit('select', {
        muscle: key,
        label: this.labels[key] || key,
        level: next,
        previousLevel: previous
      });
    },

    _onClick: function (event) {
      var group = event.target.closest ? event.target.closest('.mm-muscle') : null;
      if (group) this._activate(group);
    },

    _onKeyDown: function (event) {
      if (event.key !== 'Enter' && event.key !== ' ' && event.key !== 'Spacebar') return;
      var group = event.target.closest ? event.target.closest('.mm-muscle') : null;
      if (!group) return;
      event.preventDefault();
      this._activate(group);
    }
  };

  MuscleMap.LEVELS = LEVELS;
  MuscleMap.VIEWS = VIEWS.slice();
  MuscleMap.mount = function (target, options) { return new MuscleMap(target, options); };

  return MuscleMap;
});
