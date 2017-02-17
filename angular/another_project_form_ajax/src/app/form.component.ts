import { Component } from '@angular/core';
import { Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/toPromise';

declare var $: any;

@Component({
  moduleId: module.id,
  selector: 'form-selector',
  templateUrl: "form.component.html",
})

@Injectable()
export class FormComponent  {
	private API_POINT_SEARCH = "https://api.github.com/search/users?type=user&in=login&q=";
	private result: any[] = [];
	private result_users: any[] = [];
	private opened_github_repos: number[] = [];
	private filter_max_repos_and_users: number = 5;

	constructor (private http:Http ){}

	alert_magic(my_model: string){
		let data = this.http.get(this.API_POINT_SEARCH+my_model).toPromise()
			.then((responce)=> this.parse_result(responce));
	}

	clear_all_repos(){
		for (let i = this.opened_github_repos.length - 1; i >= 0; i--) {
			$("#"+this.opened_github_repos[i]).next().remove();
		}
		this.opened_github_repos = [];
		this.result = [];
	}

	parse_result(responce: any){
		this.clear_all_repos();
		if(responce.json().items.length > this.filter_max_repos_and_users){
			this.result_users = responce.json().items.splice(0, this.filter_max_repos_and_users);
		} else {
			this.result_users = responce.json().items;
		}
	}

	parse_individual_repo(responce: any){
		let repo = responce.json();
		console.log(repo);
		let my_ele = $("#"+repo.id);

		let parent_ul = $("<ul></ul");
		this.addToParentUl(parent_ul, repo.full_name);
		this.addToParentUl(parent_ul, repo.name);
		this.addToParentUl(parent_ul, repo.language);
		this.addToParentUl(parent_ul, "Създадено на: " + repo.created_at);
		this.addToParentUl(parent_ul, "Последна промяна на: " + repo.updated_at);

		my_ele.after(parent_ul);
	}

	getDataForRepo(repository: any){
		let index:number = this.opened_github_repos.indexOf(repository.id);
		if (index > -1){
			$("#"+repository.id).next().remove();
			this.opened_github_repos.splice(index, 1);
			return;
		}

		this.opened_github_repos.push(repository.id);
		let data = this.http.get("https://api.github.com/repos/"+repository.full_name).toPromise()
			.then((responce)=> this.parse_individual_repo(responce));
	}

	getDataForUser(user_repo_url: string){
		let data = this.http.get(user_repo_url).toPromise().then((responce) => this.populateRepos(responce))
	}

	populateRepos(repositories: any){
		this.result_users = [];
		let full_res = repositories.json();
		if(full_res.length > this.filter_max_repos_and_users){
			this.result = full_res.splice(0, this.filter_max_repos_and_users);
		} else {
			this.result = full_res;
		}
	}

	addToParentUl(parent_ul: any, text: string){
		let el = $("<li></li>");
		el.text(text);
		parent_ul.append(el);
	}

}
