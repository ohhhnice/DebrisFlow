// 控制SAM相关选项的显示与隐藏
function toggleSamOptions() {
    const useSam = document.getElementById('use_sam_true').checked;
    const samSection = document.getElementById('samParametersSection');
    const pointSection = document.getElementById('pointCoordinatesSection');

    if (useSam) {
      samSection.style.display = 'block';
      pointSection.style.display = 'block';
    } else {
      samSection.style.display = 'none';
      pointSection.style.display = 'none';
    }
  }

  // 初始调用一次来设置初始状态
  toggleSamOptions();

  // 文件夹选择函数
  function selectSaveFolder() {
    // 由于浏览器限制，无法直接获取文件夹路径
    // 让用户手动输入
    const folderPath = prompt(
      '请输入相对于项目根目录的保存文件夹路径',
      document.getElementById('save_folder').value
    );
    if (folderPath) {
      document.getElementById('save_folder').value = folderPath;
    }
  }

  // 检查点文件选择函数
  function selectCheckpointFile() {
    // 由于浏览器限制，无法直接获取文件完整路径
    // 让用户手动输入
    const filePath = prompt(
      '请输入相对于项目根目录的检查点文件路径',
      document.getElementById('sam_checkpoint').value
    );
    if (filePath) {
      document.getElementById('sam_checkpoint').value = filePath;
    }
  }

  document
    .getElementById('datasetForm')
    .addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const loading = document.getElementById('loading');

      try {
        loading.style.display = 'block';

        const response = await fetch('/generate_dataset', {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();

        if (response.ok) {
          Toastify({
            text: result.message,
            duration: 3000,
            gravity: 'top',
            position: 'right',
            backgroundColor: '#28a745',
          }).showToast();
        } else {
          throw new Error(result.error || '生成数据集失败');
        }
      } catch (error) {
        Toastify({
          text: error.message,
          duration: 3000,
          gravity: 'top',
          position: 'right',
          backgroundColor: '#dc3545',
        }).showToast();
      } finally {
        loading.style.display = 'none';
      }
    });
