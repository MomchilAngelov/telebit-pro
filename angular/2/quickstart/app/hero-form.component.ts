import {Component} from '@angular/core';

import {Hero} from './hero';

@Component({
	moduleId: module.id,
	selector: 'hero-form',
	templateUrl: './hero-form.component.html'
})
export class HeroFormComponent {

	powers = ['Умен', 'Гъвкав', 'Топъл', 'Времеразменител :^)'];

	model = new Hero(10, 'Dr. IQ', this.powers[0], "Sadness is real - the living being");

	submitted = false;

	onSubmit(){
		this.submitted = true;
	}

	get diagnostic(){
		return JSON.stringify(this.model);
	}

	newHero() {
	  this.model = new Hero(42, '', '');
	}

}