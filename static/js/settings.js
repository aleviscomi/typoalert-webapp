const domainRegex = /^(?!www)([-a-zA-Z0-9@:%._\+~#=]+\.)+[a-z]{2,6}$/;
var xhr = new XMLHttpRequest();

function addNewUserDomain() {
    var errorBanner = document.getElementById('error-banner');
    var new_domain = document.getElementById("new_domain");
    var new_domain_value = new_domain.value
    new_domain.value = "";

    if(new_domain_value) {
        if (domainRegex.test(new_domain_value)) {
            var no_domains_paragraph = document.getElementById("no-domains");

            xhr.open("POST", "/user/add/verified-domain", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        
            var formData = "domain=" + encodeURIComponent(new_domain_value);
        
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4) {
                    // add new domain to ul list
                    if (xhr.status == 200) {
                        var response = JSON.parse(xhr.responseText);
        
                        if (response.success) {
                            var ul = document.querySelector(".user-verified-domains");
                            if (!ul) {
                                var div = document.querySelector("#user-domains-list");
                                ul = document.createElement("ul");
                                ul.className = "user-verified-domains";
                                div.appendChild(ul);
                                no_domains_paragraph.style.display = "none";
                            }
                            var li = document.createElement("li");
                            li.className = "user-verified-domain";
                            var p = document.createElement("p");
                            p.textContent = new_domain_value;
                            
                            var button = document.createElement("button");
                            button.textContent = "Remove";
                            button.onclick = function() {
                                removeUserDomain(new_domain_value);
                            };
                            li.appendChild(p);
                            li.appendChild(button);
                            
                            ul.appendChild(li);

                            errorBanner.textContent = '';
                            errorBanner.style.display = 'none';
                        } else {
                            errorBanner.textContent = 'Processing errors!';
                            errorBanner.style.display = 'block';
                        }
                    } else if (xhr.status == 400) {
                        var response = JSON.parse(xhr.responseText);
                        errorBanner.textContent = response.error;
                        errorBanner.style.display = 'block';
                    }
                }
            };
        
            xhr.send(formData);
        } else {
            errorBanner.textContent = 'Invalid domain format!';
            errorBanner.style.display = 'block';
        }
    }
}


function removeUserDomain(domainName) {
    var errorBanner = document.getElementById('error-banner');
    
    xhr.open("POST", "/user/remove/verified-domain", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    // Puoi includere dati aggiuntivi nella richiesta se necessario
    var formData = "domain=" + encodeURIComponent(domainName);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);

                if (response.success) {
                    var ul = document.querySelector(".user-verified-domains");
                    var liToRemove = Array.from(ul.getElementsByClassName("user-verified-domain")).find(function(li) {
                        liName = li.querySelector("p").textContent.trim();
                        return liName === domainName;
                    });

                    if (liToRemove) {
                        liToRemove.remove();
                    }

                    if (ul.childElementCount === 0) {
                        var user_domains_list = document.getElementById("user-domains-list");
                        var no_domains_paragraph = document.getElementById("no-domains");
                        if (!no_domains_paragraph) {
                            no_domains_paragraph = document.createElement("p");
                            no_domains_paragraph.id = "no-domains";
                            no_domains_paragraph.textContent = "You don't have any domains associated with your account yet!"
                            user_domains_list.appendChild(no_domains_paragraph);
                        }
                        no_domains_paragraph.style.display = "block";
                        ul.remove();
                    }
                } else {
                    errorBanner.textContent = response.error;
                    errorBanner.style.display = 'block';
                }
            } else {
                var response = JSON.parse(xhr.responseText);
                errorBanner.textContent = response.error;
                errorBanner.style.display = 'block';
            }

        }
    };

    xhr.send(formData);
}

function copyApiKey() {
    var apiKeyField = document.getElementById('api-key');
    apiKeyField.select();
    apiKeyField.setSelectionRange(0, 99999); // For mobile devices

    navigator.clipboard.writeText(apiKeyField.value);
}