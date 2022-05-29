const download_btn = document.getElementById('download-media')
const label_download = document.getElementById('text-download')

download_btn.addEventListener('click', function(e){
    label_download.style.display = 'block'
})