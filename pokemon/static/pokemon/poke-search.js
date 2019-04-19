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

// TODO : Add a set search to pokemon that updates version. Requires the species info in the API

var poke_search = new Vue({
  el: '#poke-search',
  data: {
    search: '',
    selected_version: '',
    selected_version_info: {},
    version_info: {},
    versions: [],
    generations: [],
    pokemon_set: [],
    location_set: [],
    autocomplete: [],
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
      axios({ method: "GET", url: "/api/generations/" }).then(result => {
        this.generations = result.data;
      }, error => {
        console.error(error);
      });
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
        this.pokemon_set = [];
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
