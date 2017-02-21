import { Component, OnInit, Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions, URLSearchParams } from '@angular/http';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/toPromise';

import { Repository } from '../../models/repository'

declare var $: any;

@Component({
  moduleId: module.id,
  selector: 'login-selector',
  templateUrl: "login.component.html",
})

@Injectable()
export class LoginComponent implements OnInit  {
	private client_id:string = "4ca47a9bc303b55af5d2";
	private client_secret: string = "d6ff25620e4461c2655b75f994ba8dff40508430";
	private send_request_to_this_guy: string = "http://localhost:8888/";
	private api_request_user: string = "https://api.github.com/user?access_token=";
	private api_request_user_repos: string = "";
	private scope: string = "user%20repo";
	
	private code:string = "";
	private scopes_received: string = "";
	private access_token: string = "";
	private profile_ready: boolean = false;

	private profile_picture: string = "";
	private profile_email: string = "";
	private profile_name: string = "";
	private profile_login: string = "";

	private personal_repos: Repository[];

	private qs = (function(a) {
	    if (a.length == 0) return {};
	    var b = {};
	    for (var i = 0; i < a.length; ++i)
	    {
	        var p=a[i].split('=', 2);
	        if (p.length == 1)
	            b[p[0]] = "";
	        else
	            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
	    }
	    return b;
	})(window.location.search.substr(1).split('&'));
	
	constructor (private http:Http ){}
	

	ngOnInit() {
		this.code = this.qs['code'];

		if(this.code == undefined){
			console.log("Not yet authenticated!");
		} else {
			this.authenticate();
		}
	}

	authenticate(){
		let data = this.http.get(this.send_request_to_this_guy + this.code + "/")
			.toPromise()
			.then((responce) => this.checkResult(responce))
			.catch((responce) => this.handleError(responce));	
	}

	fetchProfileStuff(){
		let data = this.http.get(this.api_request_user+this.access_token)
			.toPromise()
			.then((responce) => this.parseProfileResults(responce))
			.catch((responce) => this.parseProfileResults(responce));
	}

	parseProfileResults(response: any){
		let data = response.json();
		this.profile_picture = data.avatar_url;
		this.profile_email = data.email;
		this.profile_name = data.name;
		this.profile_login = data.login;

		this.api_request_user_repos = data.repos_url;
		this.profile_ready = true;

		this.parseRepos();
	}

	parseRepos(){
		let data = this.http.get(this.api_request_user_repos)
			.toPromise()
			.then ( (response) => this.parsePersonalReposResults(JSON.parse(response.text()) as Repository[]) );
	}

	parsePersonalReposResultsCatcher(err: any){
		//JSON.parse(response.text()) as Repository[]
		alert("Error while fetching repositories...");
		console.log(err);
	}

	parsePersonalReposResults(personalRepositories: Repository[]) {
		this.personal_repos = personalRepositories;
	}

	checkResult(response: any){
		let data = response.json()
		if (data.access_token == undefined){
			//alertBadToken();
			return;
		}

		this.access_token = data.access_token;
		this.scopes_received = data.scope;

		this.fetchProfileStuff();
	}

	handleError(error: any){
        console.log(error);
    }
}
