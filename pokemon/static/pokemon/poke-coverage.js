function split_cap(text) {
  return text.toLowerCase().split(/[ _-]/).map((s) => s.charAt(0).toUpperCase() + s.substring(1)).join(' ');
}

function mid_slash(text) {
  unslashed = split_cap(text).split(' ');
  return unslashed.slice(0, unslashed.length/2).join(' ') + '/' + unslashed.slice(unslashed.length/2, unslashed.length).join(' ')
}

var poke_coverage = new Vue({
  el: '#poke-coverage',
  data: {
    types: [],
    matrix: {},
    selected: []
  },
  mounted:function(){
    this.onload();
  },
  methods: {
    onload:function() {
      axios({ method: "GET", "url": "/pokemon/api/type_effectiveness/" }).then(result => {
        for (var i = 0; i < result.data.length; i++) {
          if ( ! (result.data[i].attack.name in this.matrix) ) {
            this.matrix[result.data[i].attack.name] = {};
          }
          this.matrix[result.data[i].attack.name][result.data[i].defense.name] = result.data[i].effectiveness;
          this.types = ['normal', 'fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel', 'fire', 'water', 'grass', 'electric', 'psychic', 'ice', 'dragon', 'dark', 'fairy']
        }
      }, error => {
        console.error(error);
      });
    },
    select_type:function(type) {
      this.selected.push(type);
      this.selected = [...new Set(this.selected)]
    },
    unselect_type:function(type) {
      set = new Set(this.selected);
      set.delete(type);
      this.selected = [...new Set(set)];
    },
    effectiveness_style:function(effectiveness){
      if (effectiveness == 1) {
        return 'border: 1px solid black;';
      } else if (effectiveness == 0) {
        return 'color: white; background-color: black;'
      } else if (effectiveness < 1) {
        return 'color: white; background-color: red;'
      } else {
        return 'color: white; background-color: green;'
      }
    },
    split_cap:function(text) {
      return split_cap(text);
    },
    mid_slash:function(text) {
      return mid_slash(text);
    }
  },
  computed: {
    coverage:function(){
      coverage = {};
      for (i = 0; i < this.types.length; i++) {
        coverage[this.types[i]] = 0;
      }
      for (i = 0; i < this.selected.length; i++) {
        for (j = 0; j < this.types.length; j++) {
          coverage[this.types[j]] = Math.max(coverage[this.types[j]], this.matrix[this.selected[i]][this.types[j]]);
        }
      }
      coverage_list = [];
      for (type in coverage) {
        coverage_list.push({type: type, effectiveness: coverage[type]});
      }
      coverage_list.sort(function(a, b){return b.effectiveness - a.effectiveness;});
      return coverage_list;
    }
  }
})
