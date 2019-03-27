<template>
  <article class="message">
    <div class="message-header">
      <p>{{ message.id }}</p>
    </div>
    <div class="message-body">
      <pre>{{ message.data | pretty }}</pre>
    </div>
  </article>
</template>

<script>
export default {
  name: "Message",
  props: {
    message: Object
  },
  data() {
    return {
      dateOptions: {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "numeric",
        minute: "numeric"
      }
    }
  },
  filters: {
    pretty: function(value) {
      return JSON.stringify(value, null, 2)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.card {
  margin-bottom: 50px;
  border-radius: 5px;
}
</style>
