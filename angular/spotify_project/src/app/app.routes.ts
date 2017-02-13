import { provideRouter, RouterConfig } from '@angular/router'
import {searchComponent} from './components/search/search.component';
import {aboutComponent} from './components/about/about.component';


const routes: RouterConfig = [
	{path: '', component: searchComponent},
	{path: 'about', component: aboutComponent}
];

export const appRouterProviders = [
	provideRouter(routes);
];