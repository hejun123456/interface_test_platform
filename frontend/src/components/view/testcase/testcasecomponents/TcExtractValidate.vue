<template>
  <div id="tcextract">
    <div class="datarow">
      <TcExtract></TcExtract>
    </div>
    <div class="datarow">
      <TcValidate></TcValidate>
    </div>
  </div>
</template>

<script>
import TcExtract from './tcExtractVlidateComponents/TcExtract'
import TcValidate from './tcExtractVlidateComponents/TcValidate'

export default {
  name: 'tcextract',
  data () {
    return {
    }
  },
  components: {
    TcExtract,
    TcValidate
  }
}
</script>

<style lang="less" scoped>
.datarow {
  margin-bottom: 15px;
}
</style>
