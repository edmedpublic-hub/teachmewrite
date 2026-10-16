import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import {
  getAuth,
  signInAnonymously,
  signInWithCustomToken,
  onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import {
  getFirestore,
  doc,
  setDoc,
  getDoc,
  collection,
  query,
  where,
  getDocs,
  setLogLevel,
} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

// Global variables provided by the Canvas environment
const appId = typeof __app_id !== "undefined" ? __app_id : "default-app-id";
const firebaseConfig = JSON.parse(
  typeof __firebase_config !== "undefined" ? __firebase_config : "{}"
);
const initialAuthToken =
  typeof __initial_auth_token !== "undefined" ? __initial_auth_token : null;

// Initialize Firebase App, Auth, and Firestore
const app = Object.keys(firebaseConfig).length
  ? initializeApp(firebaseConfig)
  : null;
const db = app ? getFirestore(app) : null;
const auth = app ? getAuth(app) : null;

let currentUserId = null;

// 1. Authentication Setup
export const setupAuth = async () => {
  if (!auth) {
    console.error("Firebase Auth not initialized.");
    return;
  }

  // setLogLevel('debug'); // Use this if debugging auth/firestore issues

  try {
    if (initialAuthToken) {
      await signInWithCustomToken(auth, initialAuthToken);
    } else {
      await signInAnonymously(auth);
    }
    currentUserId = auth.currentUser?.uid || crypto.randomUUID();
    console.log("Firebase initialized. User ID:", currentUserId);
  } catch (error) {
    console.error("Firebase authentication failed:", error);
  }
};

// Listen for Auth changes and update the ID
if (auth) {
  onAuthStateChanged(auth, (user) => {
    currentUserId = user ? user.uid : null;
  });
}

// Helper to get the user-specific path for private data (Mastery Status)
const getMasteryDocRef = (lessonId) => {
  if (!db || !currentUserId) {
    return null;
  }
  // Path: /artifacts/{appId}/users/{userId}/mastery_status/{lessonId}
  const path = `/artifacts/${appId}/users/${currentUserId}/mastery_status`;
  return doc(db, path, lessonId);
};

// 2. Data Storage Functions
// Record a lesson as mastered
export const setLessonMastery = async (lessonId) => {
  const docRef = getMasteryDocRef(lessonId);
  if (!docRef) return false;

  try {
    await setDoc(docRef, {
      isMastered: true,
      masteredAt: new Date().toISOString(),
    });
    console.log(`Lesson ${lessonId} mastered status saved.`);
    return true;
  } catch (e) {
    console.error("Error setting mastery status:", e);
    return false;
  }
};

// Check if a lesson is mastered
export const getLessonMasteryStatus = async (lessonId) => {
  const docRef = getMasteryDocRef(lessonId);
  if (!docRef) return false;

  try {
    const docSnap = await getDoc(docRef);
    return docSnap.exists() && docSnap.data().isMastered === true;
  } catch (e) {
    console.error("Error getting mastery status:", e);
    return false;
  }
};

// Get all mastered lessons for the current user
export const getAllMasteredLessons = async () => {
  if (!db || !currentUserId) {
    return new Set();
  }
  try {
    // Path: /artifacts/{appId}/users/{userId}/mastery_status
    const collectionRef = collection(
      db,
      `/artifacts/${appId}/users/${currentUserId}/mastery_status`
    );
    const q = query(collectionRef, where("isMastered", "==", true));

    const snapshot = await getDocs(q);
    const masteredIds = new Set();
    snapshot.forEach((doc) => {
      masteredIds.add(doc.id);
    });
    return masteredIds;
  } catch (e) {
    console.error("Error fetching all mastered lessons:", e);
    return new Set();
  }
};

// Export the setup function and state for use in React components
export { setupAuth as initializeFirebase };
