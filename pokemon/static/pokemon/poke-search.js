function string_distance(a, b){
  if(a.length == 0) return b.length;
  if(b.length == 0) return a.length;

  var matrix = [];

  // increment along the first column of each row
  var i;
  for(i = 0; i <= b.length; i++){
    matrix[i] = [i];
  }

  // increment each column in the first row
  var j;
  for(j = 0; j <= a.length; j++){
    matrix[0][j] = j;
  }

  // Fill in the rest of the matrix
  for(i = 1; i <= b.length; i++){
    for(j = 1; j <= a.length; j++){
      if(b.charAt(i-1) == a.charAt(j-1)){
        matrix[i][j] = matrix[i-1][j-1];
      } else {
        matrix[i][j] = Math.min(matrix[i-1][j-1] + 1, // substitution
                                Math.min(matrix[i][j-1] + 1, // insertion
                                         matrix[i-1][j] + 1)); // deletion
      }
    }
  }

  return matrix[b.length][a.length];
};

function split(text) {
  return text.toLowerCase().split(/[ _-]/).join(' ');
}

function split_cap(text) {
  return text.toLowerCase().split(/[ _-]/).map((s) => s.charAt(0).toUpperCase() + s.substring(1)).join(' ');
}

function mid_slash(text) {
  unslashed = split_cap(text).split(' ');
  return unslashed.slice(0, unslashed.length/2).join(' ') + '/' + unslashed.slice(unslashed.length/2, unslashed.length).join(' ')
}

var poke_search = new Vue({
  el: '#poke-search',
  data: {
    search: '',
    selected_version: '',
    selected_version_info: {},
    version_info: {},
    versions: [],
    pokemon_set: [],
    location_set: [],
    autocomplete: [],
    suggestions: [],
    display: {
      stats: true,
      evo: true,
      types: false,
      moves: false,
      encounters: false,
      abilities: false
    }
  },
  mounted:function(){
    this.onload();
  },
  methods: {
    onload:function() {
      axios({ method: "GET", url: "/api/versions/" }).then(result => {
        this.versions = result.data;
      }, error => {
        console.error(error);
      });
      if ($cookies.isKey('selected_version')) {
        this.selected_version = $cookies.get('selected_version');
      }
      axios({ method: "GET", url: "/api/autocomplete/" }).then(result => {
        this.autocomplete = result.data;
        for (var i = 0; i < this.autocomplete.length; i++) {
          this.autocomplete[i] = split(this.autocomplete[i]);
        }
      }, error => {
        console.error(error);
      });
      if ($cookies.isKey('selected_version')) {
        this.selected_version = $cookies.get('selected_version');
      }
      this.load_from_url();
    },
    load_from_url:function() {
      var urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('search')) {
        this.search = urlParams.get('search');
      }
      if (urlParams.has('version')) {
        this.selected_version = urlParams.get('version');
      }
    },
    update_history:function() {
      var urlParams = new URLSearchParams(window.location.search);
      if (this.construct_query_string() != urlParams.toString()) {
        history.pushState(null, "Int. PDB", '?' + this.construct_query_string());
      }
    },
    update_suggestions:function() {
      search = this.search.toLowerCase();
      tol = Math.floor( ( search.length - 1 ) / 2 );
      suggestions = [];
      for (var i = 0; i < this.autocomplete.length; i++) {
        distance = string_distance(search, this.autocomplete[i].substring(0, this.search.length))
        if ( distance <= tol ) {
          suggestions.push({
            term: this.autocomplete[i],
            distance: string_distance(search, this.autocomplete[i].substring(0, this.search.length))
          });
        }
      }
      suggestions.sort(function(a, b){return a.distance - b.distance;});
      this.suggestions = suggestions;
    },
    update_version_info:function() {
      this.update_history();
      axios({
        method: "GET",
        url: "/api/versions/" + this.selected_version + "/"
      }).then(result => {
        this.selected_version_info = result.data;
      }, error => {
        console.error(error);
      });
    },
    update_pokemon_set:function() {
      if (this.search == '') {
        return;
      }
      if (this.selected_version == '') {
        return;
      }
      axios({
        method: "GET",
        url: "/api/pokemon/?search=" + this.search + "&version=" + this.selected_version
      }).then(result => {
        this.version_info = this.selected_version_info;
        this.pokemon_set = result.data;
      }, error => {
        console.error(error);
      });
    },
    debounced_update_pokemon_set: _.debounce(function(){
      this.update_history();
      this.update_pokemon_set();
      this.update_suggestions();
    }, 500),
    update_location_set:function() {
      if (this.search == '') {
        return;
      }
      if (this.selected_version == '') {
        return;
      }
      axios({
        method: "GET",
        url: "/api/locations/?search=" + this.search + "&version=" + this.selected_version
      }).then(result => {
        this.version_info = this.selected_version_info;
        this.location_set = result.data;
      }, error => {
        console.error(error);
      });
    },
    debounced_update_location_set: _.debounce(function(){
      this.update_location_set();
    }, 500),
    construct_query_string:function(){
      if (this.selected_version != '' && this.search != '') {
        return "version=" + this.selected_version + "&search=" + this.search;
      }
      if (this.selected_version != '') {
        return "version=" + this.selected_version;
      }
      if (this.search != '') {
        return "search=" + this.search;
      }
      return ''
    },
    set_search:function(search) {
      this.search = search;
    },
    set_version:function(version) {
      this.selected_version = version;
    },
    split_cap:function(text) {
      return split_cap(text);
    },
    mid_slash:function(text) {
      return mid_slash(text);
    },
    evo_ranks:function(evos) {
      var ranks = new Set();
      for (i = 0; i < evos.length; i++) {
        ranks.add(evos[i].evolution_rank);
      }
      return ranks;
    },
    rank_evos:function(evos, rank) {
      var ret = [];
      for (i = 0; i < evos.length; i++) {
        if (evos[i].evolution_rank == rank) {
          ret.push(evos[i]);
        }
      }
      return ret;
    },
    learn_methods:function(pokemon_moves) {
      var methods = new Set();
      for (i = 0; i < pokemon_moves.length; i++){
        methods.add(pokemon_moves[i].learn_method.name);
      }
      return methods;
    },
    method_moves:function(pokemon_moves, learn_method) {
      var moves = [];
      for (i = 0; i < pokemon_moves.length; i++) {
        if (pokemon_moves[i].learn_method.name == learn_method) {
          moves.push(pokemon_moves[i]);
        }
      }
      return moves;
    },
    stab_style:function(move, pokemon) {
      if (move.category == 'Status') {
        return '';
      }
      if (move.type.name == pokemon.primary_type.name) {
        return ' stab';
      }
      if ( (pokemon.secondary_type) && (move.type.name == pokemon.secondary_type.name) ) {
        return ' stab';
      }
      return '';
    },
    convert_if_none:function(entry, target) {
      if (entry) {
        return entry;
      }
      return target;
    }
  },
  watch: {
    selected_version: function() {
      $cookies.set('selected_version', this.selected_version);
      this.update_version_info();
      this.update_pokemon_set();
      this.update_location_set();
    },
    search: function() {
      this.debounced_update_pokemon_set();
      this.debounced_update_location_set();
    }
  }
})

window.onpopstate = function(event) {
  poke_search.load_from_url();
}

Vue.component('poke-display', {
  props: ['pokemon', 'color'],
  template: "#poke-display",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    }
  }
})

Vue.component('poke-stats', {
  props: ['pokemon'],
  template: "#poke-stats",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    }
  }
})

Vue.component('poke-evo', {
  props: ['pokemon'],
  template: "#poke-evo",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    },
    evo_ranks:function(evos) {
      var ranks = new Set();
      for (i = 0; i < evos.length; i++) {
        ranks.add(evos[i].evolution_rank);
      }
      return ranks;
    },
    rank_evos:function(evos, rank) {
      var ret = [];
      for (i = 0; i < evos.length; i++) {
        if (evos[i].evolution_rank == rank) {
          ret.push(evos[i]);
        }
      }
      return ret;
    }
  }
})

Vue.component('poke-types', {
  props: ['pokemon'],
  template: "#poke-types",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    }
  }
})

Vue.component('poke-moves', {
  props: ['pokemon', 'version_info'],
  template: "#poke-moves",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    },
    mid_slash:function(text) {
      return mid_slash(text);
    },
    learn_methods:function(pokemon_moves) {
      var methods = new Set();
      for (i = 0; i < pokemon_moves.length; i++){
        methods.add(pokemon_moves[i].learn_method.name);
      }
      return methods;
    },
    method_moves:function(pokemon_moves, learn_method) {
      var moves = [];
      for (i = 0; i < pokemon_moves.length; i++) {
        if (pokemon_moves[i].learn_method.name == learn_method) {
          moves.push(pokemon_moves[i]);
        }
      }
      return moves;
    },
    stab_style:function(move, pokemon) {
      if (move.category == 'Status') {
        return '';
      }
      if (move.type.name == pokemon.primary_type.name) {
        return ' stab';
      }
      if ( (pokemon.secondary_type) && (move.type.name == pokemon.secondary_type.name) ) {
        return ' stab';
      }
      return '';
    },
    convert_if_none:function(entry, target) {
      if (entry) {
        return entry;
      }
      return target;
    }
  }
})

Vue.component('poke-encounters', {
  props: ['pokemon', 'version_info'],
  template: "#poke-encounters",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    }
  }
})

Vue.component('poke-abilities', {
  props: ['pokemon'],
  template: "#poke-abilities",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    }
  }
})

Vue.component('location-encounters', {
  props: ['location', 'version_info'],
  template: "#location-encounters",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    }
  }
})

Vue.component('poke-inline', {
  props: ['pokemon'],
  template: "#poke-inline",
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    }
  }
})
