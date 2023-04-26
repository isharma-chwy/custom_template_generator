rx_catalog_query = """  select distinct
        vlp.agreement_number --- Hidden Field
        ,vlp.chewy_pharmacy_part_number ---Hidden Field
        ,vlp.Vendor_Number -- Hidden Field
        ,vlp.vendor_name
        ,vlp.product_part_number
        ,UPPER(p.parent_company) as parent_company
        ,p.product_manufacturer_name as brand
        ,p.product_name
        ,vlp.vendor_product_part_number
        ,Case   when vlp.vendor_uom = 'EA' then 'EACH'
                when vlp.vendor_uom = 'PK' then 'PACKAGE'
                when vlp.vendor_uom = 'CS' then 'CASE'
                when vlp.vendor_uom = 'BX' then 'BOX'
                when vlp.vendor_uom = 'PA' then 'PALLET' 
                when vlp.vendor_uom = 'B1' then 'BO1'
                when vlp.vendor_uom = 'B2' then 'BO100'
                when vlp.vendor_uom = 'B3' then 'BO1000'
                when vlp.vendor_uom = 'B11' then 'BO250'
                when vlp.vendor_uom = 'B12' then 'BO30'
                when vlp.vendor_uom = 'B13' then 'BO300'
                when vlp.vendor_uom = 'B14' then 'BO40'
                when vlp.vendor_uom = 'B16' then 'BO50'
                when vlp.vendor_uom = 'B18' then 'BO60'
                when vlp.vendor_uom = 'B21' then 'BO160'
                when vlp.vendor_uom = 'B0' then 'BO'
                when vlp.vendor_uom = 'B4' then 'BO120'
                when vlp.vendor_uom = 'B5' then 'BO150'
                when vlp.vendor_uom = 'B6' then 'BO180'
                when vlp.vendor_uom = 'B7' then 'BO200'
                when vlp.vendor_uom = 'B8' then 'BO210'
                when vlp.vendor_uom = 'B9' then 'BO240'
                when vlp.vendor_uom = 'B10' then 'BO25'
                when vlp.vendor_uom = 'B15' then 'BO400'
                when vlp.vendor_uom = 'B17' then 'BO500'
                when vlp.vendor_uom = 'B19' then 'BO90'
                when vlp.vendor_uom = 'B20' then 'BO600'
                else vlp.vendor_uom
                end as vendor_uom
        ,isnull(iuom."Qty_ per Unit of Measure",1) as vendor_uom_qty
        ,vlp.vendor_purchase_price
        ,vlp.vendor_purchase_price/isnull(iuom."Qty_ per Unit of Measure",1) as cost_per_unit
        ,isnull(vlp.product_vendor_order_multiple,0) as OM
        ,isnull(vlp.product_vendor_minimum_order_quantity,0) as MOQ
        ,vlp.manufacturer
        ,vlp.national_drug_code as NDC
        

        from chewybi.vendor_agreement_line_pharmacy vlp
        join chewybi.products_pharmacy p on p.product_part_number = vlp.product_part_number
        left join chewybi.item_unit_of_measure iuom on iuom."item No_" = vlp.chewy_pharmacy_part_number and iuom.Code = vlp.vendor_uom
        
  
        Where 1=1
        and active_agreement = 1
        and product_type <> 'ingredient'
        and p.product_company_description = 'Chewy Pharmacy'
        and p.product_discontinued_flag = 'FALSE'

"""

rx_distributor_list = """ ----Distinct list of distributor vendors----

SELECT DISTINCT vendor_name --,vendor_number

FROM
  ( SELECT DISTINCT vlp.vendor_name ,
                    vlp.Vendor_Number ,
                    vendor_distribution_method ,
                    vlp.chewy_pharmacy_part_number ,
                    vlp.product_part_number ,
                    vlp.agreement_number ,
                    vlp.vendor_product_part_number ,
                    CASE
                        WHEN vlp.vendor_uom = 'EA' THEN 'EACH'
                        WHEN vlp.vendor_uom = 'PK' THEN 'PACKAGE'
                        WHEN vlp.vendor_uom = 'CS' THEN 'CASE'
                        WHEN vlp.vendor_uom = 'BX' THEN 'BOX'
                        WHEN vlp.vendor_uom = 'PA' THEN 'PALLET'
                    END AS vendor_uom ,
                    isnull(iuom."Qty_ per Unit of Measure",1) AS vendor_uom_qty ,
                    vlp.vendor_purchase_price ,
                    vlp.vendor_purchase_price/isnull(iuom."Qty_ per Unit of Measure",1) AS cost_per_unit ,
                    isnull(vlp.product_vendor_order_multiple,0) AS OM ,
                    isnull(vlp.product_vendor_minimum_order_quantity,0) AS MOQ ,
                    vlp.national_drug_code AS NDC ,
                    vlp.manufacturer
   FROM chewybi.vendor_agreement_line_pharmacy vlp
   JOIN chewybi.products_pharmacy p ON p.product_part_number = vlp.product_part_number
   LEFT JOIN chewybi.item_unit_of_measure iuom ON iuom."item No_" = vlp.chewy_pharmacy_part_number
   AND iuom.Code = vlp.vendor_uom
   LEFT JOIN chewybi.vendors_pharmacy v ON v.vendor_number = vlp.vendor_number
   WHERE 1=1
     AND active_agreement = 1
     AND product_type <> 'ingredient'
     AND p.product_company_description = 'Chewy Pharmacy'
     AND p.product_discontinued_flag = 'FALSE' ) a
WHERE 1=1
  AND a.vendor_distribution_method = 'DISTRIBUTOR'
  AND a.vendor_name <> 'VETIQ'
"""

rx_price_query = """ ----RX Price Query----
                        SELECT product_part_number,
                        product_price_current,
                        product_map_price
                        FROM chewybi.products_pharmacy
                        WHERE 1=1
                        AND product_merch_classification2 IN ('Pharmacy')
                        AND product_is_compound IN ('false');
"""

map_edlp_query = """with a as (

        SELECT  distinct
                ag.vendor_number as site_id,
                ag.product_part_number,
                sm.vendor_name,
                ag.agreement_line_number,
                max(CASE WHEN agreement_line_start_date IS NULL THEN date('2019-07-08')
                    ELSE agreement_line_start_date END) AS agreement_line_start_date,
                ag.agreement_line_end_date,
                ag.active_agreement,
                ag.agreement_line_status,
                vt.vendor_distribution_method,
                ag.vendor_purchase_price as vendor_purchase_cost,
                ag.vendor_uom as vendor_purchase_UOM,
                pp.product_discontinued_flag,
                pp.product_published_flag,
                pp.private_label_flag,
                UPPER(pp.parent_company) as parent_company,
                UPPER(pp.product_purchase_brand) as brand,
                pp.category_owner,
                sm.vendor_number as vendor_number,
                vt.vendor_oracle_parent_number,
                pp.product_merch_classification1,
                pp.product_merch_classification2,
                pp.product_name,
                ag.vendor_product_part_number
        FROM chewybi.vendor_agreement_line ag
        LEFT JOIN chewybi.vendors vt on ag.vendor_number = vt.vendor_number
        LEFT JOIN chewybi.products_pharmacy pp on ag.product_part_number = pp.product_part_number
        LEFT JOIN sandbox_merchops.vendor_ops_automation_vendor_site_mapping sm on ag.vendor_number= sm.site_number
        WHERE 1=1
        --##change options below
                and active_agreement = TRUE
                and pp.product_discontinued_flag = FALSE
                --and ag.product_part_number = '49778' --diamond
                --and ag.vendor_number = 'P19363'
                --and sm.vendor_number = 'enter vendor supplier id'
                --and product_merch_classification2 = 'Prescription Food & Treats'
                and vendor_distribution_method in ('DIRECT', 'V2C')
        --and pp.product_part_number in ()
        --##end of conditions
        Group by 1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23
        ORDER by 1,2),


b as (

        select product_part_number, product_map_price
        from chewybi.merch_performance_snapshot
        where activity_date = current_date -1)
        --



--final output table
select distinct parent_company,vendor_name, vendor_number, site_id, brand, product_merch_classification1, a.product_part_number as Chewy_SKU, vendor_product_part_number as Vendor_part_number
from a
left join b on a.product_part_number = b.product_part_number
where parent_company in (
'MARS',
'NESTLE PURINA',
'BLUE BUFFALO COMPANY LTD',
'ROYAL CANIN',
'WELLPET',
'THE CLOROX SALES COMPANY',
'CHURCH & DWIGHT',
'HILL''S PET NUTRITION SALES',
'SMUCKER''S RETAIL FOODS')
and vendor_name !='FETCH FOR COOL PETS'


and product_merch_classification1 = 'Consumables'
"""