<template>
  <div id="app">
    <section class="section">
      <div class="container">
        <div class="columns is-8">
          <div class="column">
            <transition-group name="list" tag="div">
              <Message :message="message" v-for="message in messages" :key="message.id"/>
            </transition-group>
          </div>
        </div>
      </div>
    </section>
    <div class="footer-stats">
      <nav class="level message-stats">
        <div class="level-item has-text-centered">
          <div>
            <p class="heading">Messages</p>
            <p class="title">{{ compactInteger(counter) }}</p>
          </div>
        </div>
      </nav>
    </div>
  </div>
</template>

<script>
import Message from "./components/Message.vue"
import { db } from "./firebase"

var humanize = require("humanize-plus")

export default {
  name: "app",
  components: {
    Message
  },
  data() {
    return {
      loadTimestamp: Date.now(),
      messages: [],
      counter: 0
    }
  },
  created() {
    this.subscribeToFirestore(this.messages)
  },
  methods: {
    compactInteger: val => humanize.compactInteger(val),
    sleep: ms => {
      return new Promise(resolve => setTimeout(resolve, ms))
    },
    subscribeToFirestore: function(collectionArray) {
      db.collection("messages")
        .limit(20)
        .onSnapshot(querySnapshot => {
          var docChanges = querySnapshot.docChanges().reverse()
          docChanges.forEach(change => {
            if (change.type !== "added") {
              return
            }
            var sleepMs = 500
            this.sleep(sleepMs).then(() => {
              var message = {
                data: change.doc.data(),
                id: change.doc.id
              }
              collectionArray.unshift(message)
              this.counter++
              if (collectionArray.length > 20) {
                collectionArray.pop()
              }
            })
          })
        })
    }
  }
}
</script>

<style lang="scss" scoped>
.list-enter-active,
.list-leave-active,
.list-move {
  transition: 500ms cubic-bezier(0, 1, 0.5, 1);
  transition-property: opacity, transform;
}

.list-enter {
  opacity: 0;
  transform: translateY(-100px) scaleY(1);
}

.list-enter-to {
  opacity: 1;
  transform: translateY(0) scaleY(1);
}

.list-leave-active {
  position: absolute;
}

.list-leave-to {
  opacity: 0;
  transform: scaleY(0);
  transform-origin: center top;
}
.footer-stats {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 1) 60%
  );
  z-index: 60;
}
.message-stats {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding-bottom: 20px;
}
img.logo {
  max-height: 25px;
}
</style>