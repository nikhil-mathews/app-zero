# AppZero 

An application that transforms user-system interaction on Windows. Interprets user commands and translates them into CMD instructions, streamlining the execution of complex computer tasks with simple, natural language inputs.

- The user inputs a request into AppZero using natural language. This request can range from file management tasks to system queries or the need to send an email.

- AppZero employs OpenAI's ChatGPT API to interpret the request, understanding the intent and the necessary actions to fulfill it.

- The application then generates a JSON response that outlines the plan of action. This includes a user-friendly summary and the specific CMD commands that will execute the task.

- AppZero executes the provided CMD command in the Windows Command Prompt environment, carrying out the user's request.

- Should the task involve sending an email, AppZero utilizes a built-in email functionality to draft and send the message directly from the command line interface.

- The application provides feedback to the user in the form of terminal outputs, which can be used for further inputs or confirmation of task completion.

- ChatGPT determines if the task is completed and sets variable (Final = True) or if additional steps are required (Final = False). If the task is not final, the process loops back to step 3.

- Once the task is final, AppZero confirms with the user that their request has been satisfied.


### Simplified workflow 
<img width="1345" alt="flowchart" src="https://github.com/nikhil-mathews/app-zero/assets/52326197/e97ce8b7-18eb-4f87-95a5-d4c176631c8e">

Voice to text done locally using Whisper AI.
**youtube.com/watch?v=ABFqbY_rmEk**

###Future upgrades
Since every generated approach and answer is unique and sometimes wrong, we could have multiple threads each making a its own API call simultaneously and then all their answers evaluated and by a master to get a more "democratic" and correct one.
The downside is that it more than doubles the time taken to get a final response.
<img width="1015" alt="image" src="https://github.com/nikhil-mathews/app-zero/assets/52326197/c0063045-5419-4455-8650-656a8fcba283">
