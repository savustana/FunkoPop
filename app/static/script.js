document.getElementById("categoryList").addEventListener("click", function (){
    fetch("api/category")
        .then(response => response.json())
        .then(data => {
            let categoryList = document.getElementById("categoryList");
            categoryList.innerText = "";

            data.categories.forEach(category => {
                let li = document.createElement("li");
                li.textContent = `${category.title}`;
                categoryList.appendChild(li);
            });
        }).catch(error => console.log("Error: ", error));
});