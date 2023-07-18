
// import firebase from 'firebase/app';
// import 'firebase/firestore';

// const db = firebase.firestore();
// const chatMessagesRef = db.collection<ChatMessageDoc>('chatMessages');

// import { useEffect, useState } from "react";

// import { initializeApp } from "firebase/app";
// interface ChatMessage {

//   id: string;
//   message: string;
//   timestamp: firebase.firestore.Timestamp;
// }

// const [data, setData] = useState<ChatMessage[]>([]);

// const firebaseConfig = {
//     apiKey: process.env.FIREBASE_API_KEY,
//     authDomain: process.env.FIREBASE_AUTH_DOMAIN,
//     projectId: process.env.FIREBASE_PROJECT_ID,
//     storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
//     messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
//     appId: process.env.FIREBASE_APP_ID,
//     measurementId: process.env.FIREBASE_MEASUREMENT_ID,
// };

// if (!(firebase.apps as Array<any>).length) {
//     firebase.initializeApp(firebaseConfig);
// }

// export const Chat = () => {
//     const [data, setData] = useState([]);

//     interface ChatMessageDoc {
//     message: string;
//     timestamp: firebase.firestore.Timestamp;
//     }

//     useEffect(() => {
//     const db = firebase.firestore();

//     return db.collection<ChatMessageDoc>('chatMessages').onSnapshot((snapshot) => {
//         const newData = snapshot.docs.map((doc) => ({
//         id: doc.id,
//         ...doc.data(),
//         }));

//         setData(newData);
//     });
//     }, []);

//     return (
//         <div className="flex min-h-screen m-auto items-center justify-center bg-gray-500 text-white">
//             <div className="p-20 border border-teal-500">
//                 <p>
//                     {/* Now data is a state variable and this will cause a re-render when the API call returns. */}
//                     {JSON.stringify(data)}
//                 </p>
//             </div>
//         </div>
//     );
// };

// export default Chat;


import { useEffect, useState, React } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthUserContext';
import firebase from '../lib/clientApp'
import {Container, Row, Col, Button, Input, Form} from 'reactstrap';
import { useCollection } from "react-firebase-hooks/firestore";

const LoggedIn = () => {

  const { authUser, loading, signOut } = useAuth();
  const [post, setPost] = useState('');
  const db = firebase.firestore();
  const router = useRouter();
  const onSubmit =  (event) => {
    console.log(post)
   try {
     db.collection("posts").add({
      title : post,
    }).then((docRef) => {
      console.log("Document written with ID: ", docRef.id);
  })
} catch(error)  {
      console.error("Error adding document: ", error);
  };
    event.preventDefault()
  };
  const [posts, postsloading, postserror] = useCollection(
    firebase.firestore().collection("posts"),
    {}
  );

  // Listen for changes on loading and authUser, redirect if needed
  useEffect(() => {
    if (!loading && !authUser)
      router.push('/')
  }, [authUser, loading])
  

  return (
    <Container>
      // ...
      <Button onClick={signOut}>Sign out</Button>
      // ...
      <Col>
      <h1> Posts </h1>
      <div>
      {postserror && <strong>Error: {JSON.stringify(postserror)}</strong>}
        {postsloading && <span>Collection: Loading...</span>}      
      {posts && posts.docs.map((doc) => (
              <div>
                {JSON.stringify(doc.data())},{' '}
              </div>
            ))}
            </div>
            <Form  className="custom-form"
            onSubmit={onSubmit}>
            <Input value={post} onChange={(event) => setPost(event.target.value)} />
            <Button >Add post</Button>
            </Form>
      </Col>
    </Container>
  )
}

export default LoggedIn;