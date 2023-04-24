# A Discord Productivity Bot for aiding in project management.

![image](https://user-images.githubusercontent.com/91294189/231611798-07eb5ecc-3bb9-4781-a8d1-237e861c6525.png)

# Key Features 

## Setup 

Create a brand-new server or add to your existing server.  Add any available features to your server with a guided process that allows you to click through connections, scheduler setups, ticket systems etc. 

## Scheduler 

A robust tool to organize meetings amongst your group-members or team.  Keep track of members that have signed up, absent members, scheduled date of a meeting, and more. 

![image](https://user-images.githubusercontent.com/91294189/234134076-40fa3fcd-904e-4279-9594-d9f91d575c44.png)


## Notifier 

A notification system that allows you to connect to available connections.  Currently supports full integration with GitHub.  Allows customization of ‘type’ of notifications (which determines quantity) that get delivered straight to a Discord channel. 

## Ticket System 

A broad tool to address anything within a project.  Primarily used as a technical tool, you can create a ticket to receive support—whether that’s with technical difficulties, project difficulties, conflicts etc. 

 

# How To 

## Setup Commands 

	/setup 

The /setup command will walk you through the integration of all of our available features into your 	server.  Drop-down lists will allow you to navigate through different categories. 

## Scheduler Commands 

	/schedule 

The /schedule command will walk you through the setup of a scheduled event.  Text boxes and 		descriptions will appear for the respective fields such as event name, date etc. 

## Notifier Commands 

	/create_webhook 

The /create_webhook command generates a drop-down list to pick through available connections.  It 	then provides you with a step-by-step guide on how to manually set up notifications for these 		connections. 

	/delete_webhook 

The /delete_webhook command prompts you for a webhook source such as “GitHub.”  The command will 	then remove the webhook from the channel it’s typed in to halt all notifications to that channel. 

	/github 

The /github command prompts is an automated command to create a notification channel.  By providing 	login information and a repository, the one-step command generates an automatic connection to GitHub. 

## Ticket System Commands 

	/add 
  
The /add command allows you to add a user to a ticket—useful in situations where you want more attention on something, specific skills from a user, etc. 

	/remove 

The /remove command removes a user from the ticket.  If the ticket requires sensitive information that a user isn’t qualified to see, the /remove command can remove them off the ticket. 

 

 

 


