# predictive-whist

This is a scoring web app for Nomination Whist. It's a work-in-progress as I learn how to do things from scratch
in Django.

There will be a lot of `TODO`s dotted around, and the order of development doesn't always match what I would choose
to do on a 'real' project (e.g. there's a conspicuous lack of tests as things currently stand!).

I'm also figuring out best practice on the fly, so I'll likely come back and make some changes if I see better ways
of doing things.

Next priorities are:
- [ ] Add tests. (I was intentionally going for a 'figure things out on the fly for an MVP' approach here, but that can
   only get me so far!)
- [ ] Implement a custom User class, which only requires an email (no username) and requires the first and last name so
   that a Player can be created automatically for the User.
- [ ] Deploy this first version to GCP (switching to a Postgres DB in prod).
- [ ] Add functionality for User 'friends' (so that if a User shares their token with another User, their Players are
   both visible to each other, to enable a single Player to play games on multiple User accounts).
- [ ] Add more customisation for gameplay (there's a million varieties of scoring, round params, and special rounds,
   which aren't all currently supported).
- [ ] Make CSS customisations common (potentially downloading Bootstrap 5 instead of using `django-bootstrap-v5` and
   customising the source). There are a _lot_ of `style=...`s dotted around, which I'd love to use for custom
   classes.

This is all a bit of fun really (we play a lot of whist in our family) and is intended primarily as a learning
exercise, but the goal is definitely to get to the point where random people can sign up and use it! ☺️

It's getting there...

![image](https://github.com/richcooper95/predictive-whist/assets/58304039/271b4b64-b965-462e-8b34-190791dcad8c)

