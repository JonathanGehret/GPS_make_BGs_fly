# Old Scripts Archive

This folder contains legacy scripts that have been superseded by the professional versions but are preserved for reference and compatibility.

## 📁 **Archived Scripts**

### **Basic Plotting Scripts** (superseded by professional versions)
- `plot_2d.py` - Basic 2D static plotting
- `plot_3d.py` - Basic 3D static plotting  
- `animate_2d.py` - Basic 2D animation

### **Early Development Scripts**
- `animate_3d_fast.py` - Experimental fast 3D animation
- `animate_3d_from_csv.py` - Early CSV-based 3D animation
- `export_test_data.py` - Development utility for test data generation

### **Previous Optimization Attempts**
- `animate_live_map_optimized.py` - First optimization attempt (superseded)
- `animate_mobile_map_optimized.py` - First mobile optimization (superseded)

## 🔄 **Migration Guide**

### **Instead of old scripts, use:**

| Old Script | New Professional Version |
|------------|--------------------------|
| `plot_2d.py` | `animate_live_map_professional.py` |
| `plot_3d.py` | `animate_3d.py` (kept in main scripts) |
| `animate_2d.py` | `animate_live_map_professional.py` |
| `animate_live_map_optimized.py` | `animate_live_map_professional.py` |
| `animate_mobile_map_optimized.py` | `animate_mobile_map_professional.py` |

## 📝 **Why These Scripts Were Archived**

- **Code Quality**: Professional versions have better error handling, type hints, and documentation
- **Performance**: Professional versions include advanced optimization features
- **User Experience**: Professional versions have guided workflows and better feedback
- **Maintainability**: Professional versions follow best practices and are easier to extend
- **Functionality**: Professional versions include all features from old scripts plus enhancements

## 🔧 **If You Need to Use Old Scripts**

These scripts should still work with the current data format, but you may need to:

1. Install dependencies: `pip install -r requirements.txt`
2. Ensure data is in the correct format (CSV with semicolon separator)
3. Run from the project root directory

## ⚠️ **Note**

These archived scripts are no longer actively maintained. For new development and production use, please use the professional versions in the main `scripts/` folder.

**Recommended professional scripts:**
- `scripts/animate_live_map_professional.py` - Desktop visualization
- `scripts/animate_mobile_map_professional.py` - Mobile-optimized visualization  
- `scripts/proximity_analysis_professional.py` - Advanced proximity analysis
