# phraser
This is a rule based phrase extraction module using dependency trees. It parses a sentence using dependency parser and then based on rules extracts meaningful triples in form of meaningful phrases instead of just single words in each part of a triple. 

## Example
	### Input: { "text" : ["Sachin Bansal, Flipkart?s co-founder who minted close to a billion dollars after Walmart?s takeover of the e-commerce firm, is considering several large bets on start-ups. As per a report, Bansal is in talks with electric scooter maker Ather Energy to invest $50-100 million. Sachin, and Binny Bansal, Flipkart?s other co-founder, are the first investors in the company. The duo is said to have introduced Ather to Flipkart?s investor Lee Fixel of Tiger Global. Tiger, along with automobile maker Hero MotoCorp, invested Rs 2 billion in the company. Founded by Indian Institute of Technology (IIT), Madras alumni Tarun Mehta and Swapnil Jain, Ather is building its own line of electric scooters from ground up. The first dozen units were shipped only recently, including one that Sachin Bansal took home. ?We are in the midst of a fund-raise,? Tarun Mehta, founder and chief executive at Ather told Business Standard. He did not give specifics. Sachin Bansal made several small investments when he was at Flipkart. Now, after stepping down, he is looking to focus on large investments. Hero-backed Ather Energy launches its e-scooters starting at Rs 109,750. Last week, The Economic Times reported Bansal may invest up to a $100 million in taxi firm Ola. Mehta said Ather is in the process of ramping up operations at its production and assembly facility at Whitefield, Bangalore. ?Installed capacity (of the unit) isn?t a concern in the near term, the focus right now is to improve efficiency and make the process faster.? The company also wants to open more experience-cum-retail centres. It has only one currently in Bangalore."]}'

	### Output: "phrases": [
            [
                [
                    "subj",
                    "Sachin Bansal"
                ],
                [
                    "verb",
                    "is considering"
                ],
                [
                    "obj",
                    "several large bets on start ups"
                ]
            ],
            [
                [
                    "subj",
                    "who"
                ],
                [
                    "verb",
                    "minted after takeover of e commerce firm"
                ]
            ]
        ],
        "sentence": "Sachin Bansal, Flipkart’s co-founder who minted close to a billion dollars after Walmart’s takeover of the e-commerce firm, is considering several large bets on start-ups."
    },
    {
        "phrases": [
            [
                [
                    "subj",
                    "Bansal"
                ],
                [
                    "verb",
                    "is in talks with scooter maker Ather Energy"
                ]
            ],
            [
                [
                    "verb",
                    "to invest"
                ],
                [
                    "obj",
                    "$ 50 100 million"
                ]
            ]
        ],
        "sentence": "As per a report, Bansal is in talks with electric scooter maker Ather Energy to invest $50-100 million." ...........


# Docker Installation 
1. Install Docker 
2. Setup Docker Machine with and Ubuntu Image 16.04 - alpine
3. Go to the app folder and run command "docker build -t=<my_app_name> ." to build the app
4. Run "docker run -p 5000:5000 -d <my_app_name>" to run the app
5. Run docker-machine env to know the Host address of your docker machine
6. Now you can hit the apps api at "http://docker_host_address:5000/"
7. Hit the above address at "/extract_phrase" extension with json data as shown in example.txt to recieve the phrases as shown in example_response.txt
8. RUN THIS COOMAND FROM COMMAND LINE AFTER CHANGING THE HOST ADDRESS :
	curl -i -v -X GET -H "Content-Type:application/json" http://<docker_host_address>:5000/extract_phrase -d '{ "text" : ["Sachin Bansal, Flipkart?s co-founder who minted close to a billion dollars after Walmart?s takeover of the e-commerce firm, is considering several large bets on start-ups. As per a report, Bansal is in talks with electric scooter maker Ather Energy to invest $50-100 million. Sachin, and Binny Bansal, Flipkart?s other co-founder, are the first investors in the company. The duo is said to have introduced Ather to Flipkart?s investor Lee Fixel of Tiger Global. Tiger, along with automobile maker Hero MotoCorp, invested Rs 2 billion in the company. Founded by Indian Institute of Technology (IIT), Madras alumni Tarun Mehta and Swapnil Jain, Ather is building its own line of electric scooters from ground up. The first dozen units were shipped only recently, including one that Sachin Bansal took home. ?We are in the midst of a fund-raise,? Tarun Mehta, founder and chief executive at Ather told Business Standard. He did not give specifics. Sachin Bansal made several small investments when he was at Flipkart. Now, after stepping down, he is looking to focus on large investments. Hero-backed Ather Energy launches its e-scooters starting at Rs 109,750. Last week, The Economic Times reported Bansal may invest up to a $100 million in taxi firm Ola. Mehta said Ather is in the process of ramping up operations at its production and assembly facility at Whitefield, Bangalore. ?Installed capacity (of the unit) isn?t a concern in the near term, the focus right now is to improve efficiency and make the process faster.? The company also wants to open more experience-cum-retail centres. It has only one currently in Bangalore."]}'