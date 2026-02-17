# Dabblebase

> [!NOTE]  
> Dabblebase is still in its **beta / prerelease** phase, and documentation (including steps on how to self-host Dabblebase) is still a work-in-progress.

Dabblebase is the backend cloud platform for the classroom - enabling instructors to easily set up the backend infrastructure for their students' software engineering projects.

With Dabblebase, instructors can give their students access to a full PostgreSQL database, S3-like object storage, user authentication (with university SSO), and realtime functionality - allowing them to build feature-rich applications and gain experience using production-grade tools.

Students can also use client packages, including [**dabblebase-ts**](https://github.com/dabblebase/dabblebase-ts), to connect to Dabblebase's services.

The design and implementation of Dabblebase was the subject of my Master's paper at UNC-Chapel Hill. Access the paper [here](https://github.com/dabblebase/dabblebase/blob/main/PAPER.pdf).

## Core Features

- **Database**: Dabblebase Database provides a private, isolated database for every student project. Dabblebase provides students with database credentials they can use to connect their application backends directly to the database Instructional staff also have direct access to student databases for grading purposes and for assisting students in office hours, and student databases can be pre-populated with data tailored to specific assignments.

- **Authentication**: Dabblebase Auth manages user authentication for all student projects using UNC authentication, and students are able to configure their projects’ backends to verify that signed-in users authenticated through Dabblebase Auth.

- **Realtime**: Dabblebase Realtime exposes web socket endpoints for student projects for realtime updates. These endpoints are used for three specific purposes:
    - **Database Changes**: Student projects can listen for realtime changes to data in their database and respond to those changes in their application’s frontend.
    - **Presence**: Students can configure their projects to be able to see who is currently logged in to their apps.
    - **Broadcast**: Student projects can set up channels to send messages back and forth between clients in realtime.
With realtime support, students are able to learn about web sockets and implement them in their projects. This allows for more feature-rich projects. For example, in COMP 426, students use a combination of the realtime features above to recreate Discord, a popular social media and realtime chatting application.

- **Storage**: Dabblebase Storage provides S3-like object storage for student projects, allowing them to work with media such as image uploads in their applications.

## The Dabblebase Website

Dabblebase’s core assignment and project management features are accessible from the Dabblebase web application. This application is served from a web app server powered
by TypeScript and Next.js.

### Instructor View

On this site, instructors have the ability to manage courses and the course roster, create and publish new assignments, and access information about student projects after an assignment
has been published. The instructor’s console view shows all of the assignments they have created, their publish status, and whether or not these assignments are group or individual projects:

<img width="1693" height="1148" alt="instructor-portal" src="https://github.com/user-attachments/assets/c931d8f1-fed7-45ee-bd56-0a2a5c94b55f" />

When creating a new assignment, instructors can select whether assignments are group or individual projects and provide a setup SQL script to run on all student databases when the
assignment is published. Instructors can use this script to pre-populate tables or seed data in student databases, which may be useful for various types of assignments. Instructors can also configure groups based on their course’s roster:

<img width="1693" height="1148" alt="instructor-draft-assignment" src="https://github.com/user-attachments/assets/6a13047c-b9d0-41dd-8c05-f6de58ee9c38" />

After an assignment is published, instructors can view credentials to connect to student databases and even download the dump files for all databases, which is helpful for autograding:

<img width="1693" height="1148" alt="instructor-published-assignment" src="https://github.com/user-attachments/assets/64b2ce87-73ca-44ad-8270-253ba2435f65" />


### Student View

Students are able to see the courses they are a member of and all published assignments. When a student clicks on an assignment, they are given information about their project as well as important credentials required for them to access core Dabblebase features. These credentials include:

- **Database URL**: The direct URL to access their private PostgreSQL database provisioned by Dabblebase. Students can interact with their database by providing this database URL to any ORM of their choice.

- **Auth Verification Key**: The public verification key for the project generated by Dabblebase Auth. Students can use this key to verify that users’ authentication tokens were legitimately signed by Dabblebase’s Auth server for use with their project.

- **Project Token**: The project token, signed by Dabblebase, is used to authenticate the project with Dabblebase Storage and Dabblebase Realtime services.

These credentials are separated into different tabs like so:

<img width="1000" alt="student-portal" src="https://github.com/user-attachments/assets/01767710-d710-45ff-b178-c5a2aebd4fbf" />


The website also provides information to the student on how to use these credentials in combination with the [Dabblebase Client]() to interact with Dabblebase services in their own applications.

## Core Goals

For Dabblebase to provide value for both students and instructors, its implementation is designed around these core principles:

- **Feature-Rich Tooling**: Tools designed for pedagogical use often feel limited in capability. Dabblebase should offer the same core functionality as other BaaS services (like Supabase) to support a large variety of student projects.

- **Minimal Vendor Lock-In**: If students wish to further develop a project of theirs after a course finishes, they should be able to without having to rewrite large pieces of their app. Dabblebase should be designed in a way that makes it easy to switch to another infrastructure solution.

- **Flexible Support**: Dabblebase should be flexible enough to work with a variety of tech stacks and tools to support the pedagogical goals for a variety of different courses.

- **Features for Instructors**: Dabblebase should make it easy for instructors to create assignments with a customizable configuration to support a wide variety of assignments and courses. It should also be easy for instructional staff to access student projects and their databases for easy grading and debugging during office hours.

- **Ease of Use**: Since the core users of Dabblebase will be students who will often be
implementing backend features for the first time, Dabblebase and its APIs must be
written in a way that is easy to use, and its documentation must be presented in a way
that is digestible and accessible.

- **Pedagogical Value**: Many existing BaaS solutions design their APIs in a way that obscures how features they provide work. Without compromising on usability, Dabblebase’s APIs should be designed in a way that reveals to students the core technologies behind how features work (such as cookies / JWTs for authentication, SQL for databases, or web sockets for realtime).

- **Self-Hostable and Open Source**: Dabblebase should be able to be self-hosted by instructors or university departments so their students are able to use it. Dabblebase is a tool for educators and students alike, so it should be entirely open-source for future development.

## Self Hosting

Instructors can host Dabblebase so that they can use it in their classrooms.

*Instructions coming soon!*
