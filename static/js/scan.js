const domainRegex = /^(?!www)([-a-zA-Z0-9@:%._\+~#=]+\.)+[a-z]{2,6}$/;

function scan() {
    var loader = document.getElementById("loader");
    var scanresult = document.getElementById("scan-result");
    var domain = document.getElementById("domain").value;
    var api_key = document.getElementById("api_key").value;
    var errorBanner = document.getElementById('error-banner');

    errorBanner.textContent = '';
    errorBanner.style.display = 'none';

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/scan", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var formData = "domain=" + encodeURIComponent(domain) + "&api_key=" + encodeURIComponent(api_key);

    if (domainRegex.test(domain)) {
        loader.style.display = "block";
        scanresult.style.display = "none";
        
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                loader.style.display = "none";
                if (xhr.status == 200) {
                    scanresult.style.display = "block";
                    var response = JSON.parse(xhr.responseText);

                    renderResponse(response);
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

function renderResponse(response) {
    var scanresult = document.getElementById("scan-result");
    scanresult.innerHTML = '';
    scanresult.className = response.analysis;

    const ul = document.createElement('ul');
    ul.className = "analysis-list";

    var li;
    li = document.createElement('li');
    li.className = "analysis-item";
    li.innerHTML = `<b>Analysis:</b> <span>${response.analysis}<div style="margin-left: 5px;" class="tooltip"><i class="fa fa-info-circle tooltip-${response.analysis}"></i><span class="tooltiptext tooltiptext-${response.analysis}"></span></div></span>`;

    ul.appendChild(li);

    if (response.target) {
        li = document.createElement('li');
        li.className = "analysis-item";
        li.innerHTML = `<b>Target:</b> <span><a target="_blank" href="https://${response.target}">${response.target}</a></span>`
        ul.appendChild(li);
    }


    if (response.other_targets.length > 0) {
        li = document.createElement('li');
        li.className = "analysis-item";
        li.innerHTML = '<b>Other targets:</b>'

        var span = document.createElement('span');
        response.other_targets.forEach((t, index) => {
            span.innerHTML += `<a target="_blank" href="https://${t}">${t}</a>`;

            if (index < response.other_targets.length - 1) {
                span.innerHTML += ', ';
            }
        });
        li.appendChild(span);
        ul.appendChild(li);
    }

    var div_evaluated_on = document.createElement('div');
    div_evaluated_on.className = "scanEvaluatedDate";
    div_evaluated_on.textContent = `Evaluated on: ${response.evaluated_on}`;

    scanresult.appendChild(ul);
    scanresult.appendChild(div_evaluated_on);
}