import { Component } from '@angular/core';
import { Hero } from './hero';

@Component({
  selector: 'my-app2',
  template: `
    <h2>My favorite hero is: {{myHero.name}}</h2>
    <p>Heroes:</p>
    <ul>
      <li *ngFor="let hero of heroes">
        {{ hero.name }}
      </li>
    </ul>
    <p *ngIf="heroes.length > 3">There are many heroes!</p>
    <h1>Hello {{ name }}</h1>
    <h1>Pressed: {{ num }}</h1>
    <button (click) = "this_method()">Button</button>
    <p>{{val}}</p>
    <input #value_inputter 
      (keyup.enter) = "this_method2(value_inputter.value)" 
      (blur) = "this_method3(value_inputter.value)" />
  	`
})
export class SwagComponent  { 
	name: string = "Momchil";
  val: string = "";
  num: number = 0;
  id:number = 21;


  heroes = [
    new Hero(1, 'Windstorm'),
    new Hero(13, 'Bombasto'),
    new Hero(15, 'Magneta'),
    new Hero(20, 'Tornado')
  ];
  myHero = this.heroes[0];


  this_method() {
    this.num++;
  }

  this_method2(value: string) {
    this.val += value;
    let my_hero = new Hero(this.id, value);
    this.heroes.push(my_hero);
    this.id += 1;
  }

  this_method3(value: string){
    alert("Value will be submitted even with u not pressing enter...");
    this.this_method2(value);
  }

}
