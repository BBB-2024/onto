class Point {
    constructor(x,y) {
        this.x = x;
        this.y = y;
    }
}

class City {
    constructor(position,size) {
        this.position = position;
        this.size = size;
    }
}

class Road {
    constructor(start,end,cities) {
        this.start = start;
        this.end = end;
        this.cities = cities;
    }
}

function index() { 
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = () => {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            let response = JSON.parse(xhttp.response);
            console.log(response);
            let responseData = {
                original_data:response.data,
                id:response.data.ID,
                teamcode:"be98b0b567b9887e75e5",
                original_hash:response.hash,
                answer_data:[]
            };
            response.data.questions.forEach((element)=>{
                let question = element;
                let varos = 0;
                let ut = 0;
                let utszakasz = 0;

                let answer = [varos, ut, uts];


                responseData.answer_data.push({
                    'id':element.ID,
                    'answer':answer
                });
            });
            console.log(responseData);
            let xhr = new XMLHttpRequest();
            xhr.onreadystatechange = ( ) => {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    console.log(xhr.response);
                }
            }
            xhr.open('POST','http://bitkozpont.mik.uni-pannon.hu/2024/answer.php',true)
            xhr.send(JSON.stringify(responseData));
        }
    }
    xhttp.open('POST','http://bitkozpont.mik.uni-pannon.hu/2024/gettasks.php',true);
    xhttp.send(JSON.stringify(
        {
            id:'2',
            teamcode:'be98b0b567b9887e75e5'
        }
    ));
}
index();