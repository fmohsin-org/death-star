package com.deathstar.supply.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "supply_items")
public class SupplyItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String itemName;

    @Column(length = 1000)
    private String description;

    @Column(nullable = false)
    private String category;

    private BigDecimal unitPrice;

    private BigDecimal totalCost;

    private Integer quantity;

    private Integer reorderThreshold;

    @Column(nullable = false)
    private String supplierId;

    private String supplierName;

    private String warehouseLocation;

    @Column(name = "is_classified")
    private Boolean isClassified;

    private String classificationLevel;

    @Column(name = "kyber_crystal_grade")
    private String kyberCrystalGrade;

    private String tibannaGasPurity;

    private BigDecimal discountPercentage;

    private BigDecimal overridePrice;

    @Column(name = "approved_by")
    private String approvedBy;

    @Column(name = "priority_level")
    private String priorityLevel;

    private Boolean exemptFromAudit;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getItemName() { return itemName; }
    public void setItemName(String itemName) { this.itemName = itemName; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public BigDecimal getUnitPrice() { return unitPrice; }
    public void setUnitPrice(BigDecimal unitPrice) { this.unitPrice = unitPrice; }

    public BigDecimal getTotalCost() { return totalCost; }
    public void setTotalCost(BigDecimal totalCost) { this.totalCost = totalCost; }

    public Integer getQuantity() { return quantity; }
    public void setQuantity(Integer quantity) { this.quantity = quantity; }

    public Integer getReorderThreshold() { return reorderThreshold; }
    public void setReorderThreshold(Integer reorderThreshold) { this.reorderThreshold = reorderThreshold; }

    public String getSupplierId() { return supplierId; }
    public void setSupplierId(String supplierId) { this.supplierId = supplierId; }

    public String getSupplierName() { return supplierName; }
    public void setSupplierName(String supplierName) { this.supplierName = supplierName; }

    public String getWarehouseLocation() { return warehouseLocation; }
    public void setWarehouseLocation(String warehouseLocation) { this.warehouseLocation = warehouseLocation; }

    public Boolean getIsClassified() { return isClassified; }
    public void setIsClassified(Boolean isClassified) { this.isClassified = isClassified; }

    public String getClassificationLevel() { return classificationLevel; }
    public void setClassificationLevel(String classificationLevel) { this.classificationLevel = classificationLevel; }

    public String getKyberCrystalGrade() { return kyberCrystalGrade; }
    public void setKyberCrystalGrade(String kyberCrystalGrade) { this.kyberCrystalGrade = kyberCrystalGrade; }

    public String getTibannaGasPurity() { return tibannaGasPurity; }
    public void setTibannaGasPurity(String tibannaGasPurity) { this.tibannaGasPurity = tibannaGasPurity; }

    public BigDecimal getDiscountPercentage() { return discountPercentage; }
    public void setDiscountPercentage(BigDecimal discountPercentage) { this.discountPercentage = discountPercentage; }

    public BigDecimal getOverridePrice() { return overridePrice; }
    public void setOverridePrice(BigDecimal overridePrice) { this.overridePrice = overridePrice; }

    public String getApprovedBy() { return approvedBy; }
    public void setApprovedBy(String approvedBy) { this.approvedBy = approvedBy; }

    public String getPriorityLevel() { return priorityLevel; }
    public void setPriorityLevel(String priorityLevel) { this.priorityLevel = priorityLevel; }

    public Boolean getExemptFromAudit() { return exemptFromAudit; }
    public void setExemptFromAudit(Boolean exemptFromAudit) { this.exemptFromAudit = exemptFromAudit; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
