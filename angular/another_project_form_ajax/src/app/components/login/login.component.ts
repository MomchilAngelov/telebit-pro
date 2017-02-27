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
	private send_request_to_this_guy: string = "http://127.0.0.1:8888/";
	private api_request_user: string = "https://api.github.com/user?access_token=";
	private api_request_user_without_token_in_url: string = "https://api.github.com/user";
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
	private currentDirectory: Directory;

	private personal_repos: Repository[];
	private selectedRepo: Repository;
	private selectedFolders: Directory[] = [];
	private selectedFiles: File[] = [];
	private newFile: File;
	private newFileSelected: boolean = false;

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
		let pathToContentRepo = this.api_request_single_repository + this.user.login + "/"
			 + this.selectedRepo.name + "/contents/"

		this.currentDirectory = new Directory();
		this.currentDirectory.url = pathToContentRepo;
		let data = this.http.get(pathToContentRepo)
		.toPromise()
		.then((response) => this.parseResponceFromFolder(response, response.json() as File[]))
		.catch(function(response){
			console.log(response);
		})
	}

	checkForUpdates(){
		return !(this.isFileSelected || this.newFileSelected);
	}

	reloadDirectory(){
		this.getFolder(this.currentDirectory);
	}

	parseResponceFromFolder(response:any, files: File[]){
		this.isFileSelected = false;
		this.selectedFile = undefined;
		this.newFile = undefined
    	this.newFileSelected = false;
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
		.then((response) => this.parseResponceFromFolder(response, response.json() as File[]))
		.catch(function(response){
			console.log(response);
		});
	}

	getFolderFromView(directory: Directory){
		this.depth += 1;
		this.getFolder(directory);
		this.currentDirectory = directory;
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
		this.selectedFile = undefined;
		this.newFile = undefined
    	this.newFileSelected = false;
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
	
	saveFileCall(file: File){
		let data = this.http.post(this.send_request_to_this_guy + "generate-sha1-github-style/",
			 JSON.stringify({"text": btoa(encodeURIComponent(file.decodedContent))}))
			.toPromise()
			.then((response) => this.saveFile(response, this.selectedFile))
			.catch(function(response){
				console.log("Calling from error of saveFileCall...");
				console.log(response);
			});
	}

    saveFile(response: any, file: File){
    	let headers = new Headers();
		headers.append('Authorization', `token ${this.access_token}`);

		let options = new RequestOptions({ headers: headers });

    	let body = JSON.stringify({
    		sha: file.sha,
			//sha: response._body,
    		path: file.url,
    		message: "Updaing!",
    		content: btoa(encodeURIComponent(file.decodedContent)),
   		});

    	console.log(body);

    	let data = this.http.put(file.url, body, options)
	    	.toPromise()
	    	.then((response) => this.saveFileComplete(response.json().content as File, file))
	    	.catch(function(response){
	    		console.log("Called from the catch section of saveFile request to update the file...");
	    		console.log(response);
	    	})
    }

    saveFileComplete(request_return_file: File, file: File){
    	file.sha = request_return_file.sha;
    	this.reloadDirectory();
    	alert('Файла беше запазен успешно!\n'+file.html_url);
    }

    createFile(){
    	let file = new File();
    	file.decodedContent = "Съдържание на новия файл...";
    	file.name = "Име на новия файл...";
    
		this.newFile = file;
    	this.newFileSelected = true;	
    }

    createFileCall(file: File){
    	console.log(this.currentDirectory.url);
    	
    	let headers = new Headers();
		headers.append('Authorization', `token ${this.access_token}`);
		let options = new RequestOptions({ headers: headers });

		console.log(file);
		console.log(this.currentDirectory.url + file.name);

    	let body = JSON.stringify({
    		path: this.currentDirectory.url + file.name,
    		message: "Creating new file with the help of the github api...",
    		content: btoa(encodeURIComponent(file.decodedContent)),
   		});

    	let data = this.http.put(this.currentDirectory.url + file.name, body, options)
    	.toPromise()
    	.then((response) => this.createdNewFile(response))
    	.catch(function(response){
    		console.log(response);
    	})

    }

    createdNewFile(response: any){
    	this.reloadDirectory();
    	console.log(response);
    	alert("Successfull New File GENERATION!");
    }

    deleteFile(file: File){
    	let body = JSON.stringify({
    		path: file.url,
    		message: "Deleting a file with the help of the github api...",
    		sha: file.sha
    	});

    	let headers = new Headers();
		headers.append('Authorization', `token ${this.access_token}`);
		let options = new RequestOptions({ headers: headers, method: "DELETE", body: body });

    	let data = this.http.request(file.url, options)
    	.toPromise()
    	.then((response)=>this.deletedFileSuccess(response))
    	.catch(function (response) {
    		console.log(response);
    	})
    }

    deletedFileSuccess(response: any){
    	console.log(response);
    	alert("File successfully deleted...");
    	this.reloadDirectory();
    }

    updateUserInformation(user: User){
    	let body = JSON.stringify(user);

    	let headers = new Headers();
		headers.append('Authorization', `token ${this.access_token}`);
		let options = new RequestOptions({ headers: headers, method: "PATCH", body: body });

    	let data = this.http.request(this.api_request_user_without_token_in_url, options)
    	.toPromise()
    	.then((response) => this.updateUserSuccess(response))
    	.catch(function(response){
    		console.log(response);
    	})
    	console.log(user.name);
    }

    updateUserSuccess(response: any){
    	console.log(response);
    	alert("User was updated successfully!...");
    }
}
