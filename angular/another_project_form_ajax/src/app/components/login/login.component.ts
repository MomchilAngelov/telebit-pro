import { Component, OnInit, Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions, URLSearchParams } from '@angular/http';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/toPromise';

import { Repository } from '../../models/repository/repository';
import { User } from '../../models/user/user';
import { Directory } from '../../models/directory/directory';
import { File } from '../../models/file/file';

declare var $: any;

@Component({
  moduleId: module.id,
  selector: 'login-selector',
  templateUrl: "login.component.html",
  styleUrls: ["login.component.css", ]
})

@Injectable()
export class LoginComponent implements OnInit  {
	private client_id:string = "4ca47a9bc303b55af5d2";
	private client_secret: string = "d6ff25620e4461c2655b75f994ba8dff40508430";
	private send_request_to_this_guy: string = "http://localhost:8888/";
	private api_request_user: string = "https://api.github.com/user?access_token=";
	private api_request_user_repos: string = "";
	private api_request_single_repository: string = "https://api.github.com/repos/";

	private scope: string = "user%20repo";
	
	private code:string = "";
	private scopes_received: string = "";
	private access_token: string = "";
	private profile_ready: boolean = false;

	private user: User;
	private isFileSelected: boolean = false;
	private selectedFile: File;
	private notRootDirectory: boolean = false;
	private depth: number = 0;

	//In the case of an empty folder...
	private lastDirectory: Directory;

	private personal_repos: Repository[];
	private selectedRepo: Repository;
	private selectedFolders: Directory[] = [];
	private selectedFiles: File[] = [];

	private qs = (function(a) {
	    if (a.length == 0) return {};
	    let b = {};
	    for (let i = 0; i < a.length; ++i)
	    {
	        let p = a[i].split('=', 2);
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

	onSelect(repository: Repository) {
		this.depth = 0;
		this.selectedRepo = repository;
		let data = this.http.get(this.api_request_single_repository + this.user.login + "/"
			 + this.selectedRepo.name + "/contents/")
		.toPromise()
		.then((responce) => this.parseResponceFromFolder(responce.json() as File[]))
		.catch(function(responce){
			console.log(responce);
		})
	}

	parseResponceFromFolder(files: File[]){
		this.isFileSelected = false;
		this.selectedFile = undefined;
		this.selectedFolders = [];
		this.selectedFiles = [];
		for (var i = files.length - 1; i >= 0; i--) {
			if(files[i].size == 0){
				this.selectedFolders.push(files[i]);
			} else {
				this.selectedFiles.push(files[i]);
			}
		}

	}

	getFolder(directory: Directory){
		let data = this.http.get(directory.url)
		.toPromise()
		.then((response) => this.parseResponceFromFolder(response.json() as File[]))
		.catch(function(response){
			console.log(response);
		});
	}

	getFolderFromView(directory: Directory){
		this.depth += 1;
		this.getFolder(directory);
		this.notRootDirectory = true;

		let temp = new Directory();
		temp.url = directory.url.substring(0, directory.url.lastIndexOf("/"));
		this.lastDirectory = temp;

	}

	getFile(file: File){
		this.isFileSelected = true;
		this.selectedFile = file;
		this.selectedFile.decodedContent = atob(this.selectedFile.content);
	}	

	returnFromFile(){
		this.isFileSelected = false;
	}

	returnFromFolder(){
		this.depth -= 1;
		if(this.depth == 0){
			this.notRootDirectory = false;
		}
		let directory = this.lastDirectory;
		let temp = new Directory();
		temp.url = this.lastDirectory.url.substring(0, this.lastDirectory.url.lastIndexOf("/"));
		this.lastDirectory = temp;

		this.getFolder(directory);
	}

	fetchFile(file: File){
		let data = this.http.get(file.url)
		.toPromise()
		.then((response) => this.getFile(response.json() as File))
		.catch(function(response){
			console.log(response);
		});
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
		this.user = response.json() as User;

		this.api_request_user_repos = this.user.repos_url;
		this.profile_ready = true;

		this.parseRepos();
	}

	parseRepos(){
		let data = this.http.get(this.api_request_user_repos)
			.toPromise()
			.then ( (response) => this.parsePersonalReposResults(JSON.parse(response.text()) as Repository[]) );
	}

	parsePersonalReposResultsCatcher(err: any){
		//JSON.parse(response.text()) as Repository[];
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
