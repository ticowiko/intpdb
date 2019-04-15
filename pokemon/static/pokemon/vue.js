function split_cap(text) {
  return text.toLowerCase().split(/[ _-]/).map((s) => s.charAt(0).toUpperCase() + s.substring(1)).join(' ');
}

function mid_slash(text) {
  unslashed = split_cap(text).split(' ');
  return unslashed.slice(0, unslashed.length/2).join(' ') + '/' + unslashed.slice(unslashed.length/2, unslashed.length).join(' ')
}

var app = new Vue({
  el: '#app',
  data: {
    search: '',
    selected_version: '',
    selected_version_info: {},
    version_info: {},
    versions: [],
    pokemon_set: [],
    version: {}
  },
  mounted:function(){
    this.onload()
  },
  methods: {
    onload:function(){
      axios({ method: "GET", "url": "/pokemon/api/versions/" }).then(result => {
        this.versions = result.data;
      }, error => {
        console.error(error);
      });
    },
    update_version_info:function(){
      axios({
        method: "GET",
        "url": "/pokemon/api/versions/" + this.selected_version + "/"
      }).then(result => {
        this.selected_version_info = result.data;
      }, error => {
        console.error(error);
      });
    },
    update_pokemon_set:function(){
      axios({
        method: "GET",
        "url": "/pokemon/api/pokemon/?search=" + this.search + "&version=" + this.selected_version
      }).then(result => {
        this.version_info = this.selected_version_info;
        this.pokemon_set = result.data;
      }, error => {
        console.error(error);
      });
    },
    debounced_update_pokemon_set: _.debounce(function(){
      this.update_pokemon_set();
    }, 500),
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
      this.update_version_info();
      this.debounced_update_pokemon_set();
    },
    search: function() {
      this.debounced_update_pokemon_set();
    }
  }
})

Vue.component('poke-display', {
  props: ['pokemon', 'color'],
  template: `
    <figure class="poke-display" v-bind:style="'background-color: ' + color">
        <img v-bind:src="pokemon.sprite_url" v-bind:alt="pokemon.form_name" class="poke-sprite">
        <figcaption class="poke-caption">
            <table style="text-align:center">
                <tr>
                    <th colspan="2">
                        {{ split_cap(pokemon.form_name) }}
                    </th>
                </tr>
                <tr>
                    <td v-bind:class="pokemon.primary_type.name + ' type-sprite'">
                        {{ split_cap(pokemon.primary_type.name) }}
                    </td>
                    <td v-if="pokemon.secondary_type" v-bind:class="pokemon.secondary_type.name + ' type-sprite'">
                        {{ split_cap(pokemon.secondary_type.name) }}
                    </td>
                </tr>
            </table>
        </figcaption>
    </figure>
  `,
  methods: {
    split_cap:function(text) {
      return split_cap(text);
    }
  }
})
